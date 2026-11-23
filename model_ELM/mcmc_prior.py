"""Versioned physical priors and sampler geometry for 18-parameter MCMC.

The physical-space density is authoritative.  ``sampler_log_density`` adds
the change-of-variables Jacobian only for samplers operating in transformed
coordinates.  PPE2 support is implemented for testing but is deliberately
incompatible with the published PPE1 coupled surrogate.
"""
from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np

from .mcmc_geometry import CoordinateTransform


PARAMETER_NAMES = (
    "k_l1", "k_l2", "k_l3", "k_s1", "k_s2", "k_s3", "k_s4", "k_frag",
    "rf_l1s1", "rf_l2s2", "rf_l3s3", "rf_s1s2", "rf_s2s3", "rf_s3s4",
    "act25", "leaf_long", "leafcn", "frootcn",
)
LOG_PARAMETERS = frozenset(PARAMETER_NAMES[:8])
PPE1 = "ppe1"
PPE2 = "ppe2"
SUPPORTED_PRIORS = (PPE1, PPE2)
CN_GAP = 0.5
LIVEWOOD_CN = 50.0
PPE2_KS4_LOW = 8.0e-5
PPE2_KS4_HIGH_CAP = 1.0e-3

EXPECTED_FILE_HASHES = {
    PPE1: {
        "NEON_ppe_vertc_parmfile": "5dac81e5a00088e9d8e94b88f4805bc16076a51f1895cf2e5f78a6382e243718",
        "SAMPLING.md": "552f28431994c01d821ac722dd111ad6d6d11e53e6a0c6fe0f585d6eb5c6ff3d",
        "generate_scramble_sobol.py": "c3b64ebdd4116ff7aff6c3c4ecc2ac2351f2b275c58cc84be9074ffcdcf88cf2",
        "sobol18_1024.txt": "d73737cb48535037a101cbef641b65c22f82a7cf507956d8e12ec48c98087000",
        "sobol18_1024_unit.txt": "18587ea351008ba4eff6f6b68ed83a619bd18c42ac6f3118cdea2e170185addc",
        "sobol18_1024_names.txt": "828532016d779aafa817e0b3b11dee39544da9cd80f4ecb0e94182e41aed6abe",
        "sobol18_1024_meta.json": "80a6ed8403df389b746d33aef389dde3f89754d94df9f74953acce98dd400e0a",
    },
    PPE2: {
        "NEON_ppe2_vertc_parmfile": "77faf93901e6cb0d7a8d8f31ed161161d573ac26f12515b36e61f979ecea87bf",
        "SAMPLING.md": "8e3b20ab195ee243636e6b5c8d7e9c459ec81e2671ebfd050d66a95634d9edde",
        "generate_scramble_sobol.py": "5cd75435ec8f4c978e9e4f82b220f25b8e95836076ef2f17a58653340d67ef8c",
        "sobol18_1024.txt": "fc5524902e98b801f5130147779eb38f44695143b1f30e10555e7a8156905b23",
        "sobol18_1024_unit.txt": "18587ea351008ba4eff6f6b68ed83a619bd18c42ac6f3118cdea2e170185addc",
        "sobol18_1024_names.txt": "828532016d779aafa817e0b3b11dee39544da9cd80f4ecb0e94182e41aed6abe",
        "sobol18_1024_meta.json": "b4f155806042e11e4f7de68f020bd4b2a3349dd1b2f24b48820b345ec49336db",
    },
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_parameter_file(path: Path) -> tuple[tuple[str, ...], np.ndarray, np.ndarray, np.ndarray]:
    rows = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            fields = line.split()
            if len(fields) < 4:
                raise ValueError(f"malformed parameter row: {raw!r}")
            rows.append((fields[0], int(fields[1]), float(fields[2]), float(fields[3])))
    if len(rows) != 18:
        raise ValueError("parameter file must contain exactly 18 rows")
    names = tuple(row[0] for row in rows)
    if names != PARAMETER_NAMES:
        raise ValueError("parameter order does not match the canonical PPE order")
    pfts = np.asarray([row[1] for row in rows], dtype=np.int64)
    lower = np.asarray([row[2] for row in rows], dtype=np.float64)
    upper = np.asarray([row[3] for row in rows], dtype=np.float64)
    if np.any(~np.isfinite(lower)) or np.any(~np.isfinite(upper)) or np.any(upper <= lower):
        raise ValueError("parameter bounds must be finite and strictly ordered")
    return names, pfts, lower, upper


@dataclass(frozen=True)
class Prior18:
    prior_id: str
    names: tuple[str, ...]
    pft_indices: np.ndarray
    lower: np.ndarray
    upper: np.ndarray
    parameter_file: Path
    generator_file: Path
    metadata_file: Path
    sampling_note: Path | None

    @classmethod
    def from_directory(cls, prior_id: str, directory: Path | str) -> "Prior18":
        if prior_id not in SUPPORTED_PRIORS:
            raise ValueError(f"unsupported prior_id: {prior_id}")
        root = Path(directory).resolve()
        parameter_name = "NEON_ppe_vertc_parmfile" if prior_id == PPE1 else "NEON_ppe2_vertc_parmfile"
        parameter_file = root / parameter_name
        generator_file = root / "generate_scramble_sobol.py"
        metadata_file = root / "sobol18_1024_meta.json"
        sampling_note = root / "SAMPLING.md"
        expected_hashes = EXPECTED_FILE_HASHES[prior_id]
        required = [root / name for name in expected_hashes]
        if not all(path.is_file() for path in required):
            missing = [str(path) for path in required if not path.is_file()]
            raise ValueError(f"missing authoritative prior files: {missing}")
        for name, expected in expected_hashes.items():
            if _sha256(root / name) != expected:
                raise ValueError(f"authoritative {prior_id} input identity mismatch: {name}")
        names, pfts, lower, upper = _read_parameter_file(parameter_file)
        metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
        if tuple(metadata.get("parameter_names", ())) != names:
            raise ValueError("metadata parameter order mismatch")
        if list(metadata.get("pft_indices", ())) != pfts.tolist():
            raise ValueError("metadata PFT indices mismatch")
        transforms = metadata.get("transforms", ())
        if len(transforms) != 18:
            raise ValueError("metadata must declare 18 transforms")
        for index, item in enumerate(transforms):
            if item.get("name") != names[index]:
                raise ValueError("metadata transform order mismatch")
            if float(item["lower"]) != lower[index] or float(item["upper"]) != upper[index]:
                raise ValueError("metadata bounds mismatch")
        cn = metadata.get("cn_constraint", {})
        if not cn.get("enabled") or int(cn.get("leafcn_index", -1)) != 16 or int(cn.get("frootcn_index", -1)) != 17:
            raise ValueError("conditional C:N metadata mismatch")
        if float(cn.get("gap", np.nan)) != CN_GAP or float(cn.get("livewoodcn", np.nan)) != LIVEWOOD_CN:
            raise ValueError("conditional C:N constants mismatch")
        if prior_id == PPE1:
            if lower[6] != 2.0e-5 or upper[6] != 2.0e-4:
                raise ValueError("PPE1 k_s4 bounds mismatch")
            if transforms[6].get("prior") != "log_uniform":
                raise ValueError("PPE1 k_s4 transform mismatch")
        else:
            ks4 = metadata.get("ks4_constraint", {})
            if not ks4.get("enabled") or float(ks4.get("low", np.nan)) != PPE2_KS4_LOW:
                raise ValueError("PPE2 k_s4 conditional metadata mismatch")
            if float(ks4.get("high_cap", np.nan)) != PPE2_KS4_HIGH_CAP:
                raise ValueError("PPE2 k_s4 ceiling mismatch")
            if transforms[6].get("prior") != "conditional_log_uniform_ks4":
                raise ValueError("PPE2 k_s4 transform mismatch")
        return cls(prior_id, names, pfts, lower, upper, parameter_file, generator_file, metadata_file, sampling_note)

    @property
    def coordinate_transform(self) -> CoordinateTransform:
        return CoordinateTransform.from_parameters(self.names, self.lower, self.upper, enabled=True)

    def _matrix(self, values: Sequence[float] | np.ndarray) -> tuple[np.ndarray, bool]:
        array = np.asarray(values, dtype=np.float64)
        scalar = array.ndim == 1
        if scalar:
            array = array.reshape(1, -1)
        if array.ndim != 2 or array.shape[1] != 18:
            raise ValueError("parameter values must have shape (18,) or (n,18)")
        return array, scalar

    def cn_bounds(self, leafcn: np.ndarray | float) -> tuple[np.ndarray, float]:
        low = np.maximum(self.lower[17], np.asarray(leafcn, dtype=np.float64) + CN_GAP)
        high = min(self.upper[17], LIVEWOOD_CN - CN_GAP)
        return low, float(high)

    def ks4_bounds(self, ks3: np.ndarray | float) -> tuple[np.ndarray, np.ndarray]:
        value = np.asarray(ks3, dtype=np.float64)
        if self.prior_id == PPE1:
            return np.full_like(value, self.lower[6]), np.full_like(value, self.upper[6])
        return np.full_like(value, PPE2_KS4_LOW), np.minimum(PPE2_KS4_HIGH_CAP, value)

    def inverse_unit(self, unit: np.ndarray | Sequence[float]) -> np.ndarray:
        u, scalar = self._matrix(unit)
        if np.any(~np.isfinite(u)) or np.any(u < 0.0) or np.any(u > 1.0):
            raise ValueError("unit coordinates must be finite in [0,1]")
        physical = self.lower + u * (self.upper - self.lower)
        for index, name in enumerate(self.names):
            if name in LOG_PARAMETERS:
                physical[:, index] = np.exp(
                    np.log(self.lower[index]) + u[:, index] * np.log(self.upper[index] / self.lower[index])
                )
        if self.prior_id == PPE2:
            low, high = self.ks4_bounds(physical[:, 5])
            if np.any(high <= low):
                raise ValueError("PPE2 k_s4 conditional interval is empty")
            physical[:, 6] = np.exp(np.log(low) + u[:, 6] * np.log(high / low))
        root_low, root_high = self.cn_bounds(physical[:, 16])
        if np.any(root_low >= root_high):
            raise ValueError("conditional C:N interval is empty")
        physical[:, 17] = root_low + u[:, 17] * (root_high - root_low)
        return physical[0] if scalar else physical

    def support_mask(self, values: np.ndarray | Sequence[float]) -> np.ndarray | bool:
        matrix, scalar = self._matrix(values)
        valid = np.all(np.isfinite(matrix), axis=1)
        valid &= np.all(matrix >= self.lower, axis=1) & np.all(matrix <= self.upper, axis=1)
        root_low, root_high = self.cn_bounds(matrix[:, 16])
        valid &= (root_low < root_high) & (matrix[:, 17] >= root_low) & (matrix[:, 17] <= root_high)
        ks4_low, ks4_high = self.ks4_bounds(matrix[:, 5])
        valid &= (ks4_low < ks4_high) & (matrix[:, 6] >= ks4_low) & (matrix[:, 6] <= ks4_high)
        return bool(valid[0]) if scalar else valid

    def log_density(self, values: np.ndarray | Sequence[float]) -> np.ndarray | float:
        matrix, scalar = self._matrix(values)
        valid = np.asarray(self.support_mask(matrix), dtype=bool)
        result = np.full(matrix.shape[0], -np.inf, dtype=np.float64)
        if np.any(valid):
            selected = matrix[valid]
            logp = np.zeros(selected.shape[0], dtype=np.float64)
            for index, name in enumerate(self.names):
                if name in LOG_PARAMETERS and not (self.prior_id == PPE2 and index == 6):
                    logp -= np.log(selected[:, index]) + np.log(np.log(self.upper[index] / self.lower[index]))
                elif index not in (6, 17):
                    logp -= np.log(self.upper[index] - self.lower[index])
            if self.prior_id == PPE2:
                low, high = self.ks4_bounds(selected[:, 5])
                logp -= np.log(selected[:, 6]) + np.log(np.log(high / low))
            root_low, root_high = self.cn_bounds(selected[:, 16])
            logp -= np.log(root_high - root_low)
            result[valid] = logp
        return float(result[0]) if scalar else result

    def sampler_log_density(self, sampler: np.ndarray | Sequence[float]) -> np.ndarray | float:
        coordinate = np.asarray(sampler, dtype=np.float64)
        physical = self.coordinate_transform.sampler_to_physical(coordinate)
        density = self.log_density(physical)
        jacobian = self.coordinate_transform.log_abs_det_dphysical_dsampler(coordinate)
        value = np.asarray(density) + jacobian
        return float(value) if value.ndim == 0 else value

    def require_release_compatibility(self, release_prior_id: str) -> None:
        if release_prior_id != PPE1:
            raise ValueError(f"unsupported release prior identity: {release_prior_id}")
        if self.prior_id != release_prior_id:
            raise ValueError(
                f"prior/release incompatibility: prior_id={self.prior_id}, release_prior_id={release_prior_id}"
            )

