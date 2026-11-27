"""Checkpointed, audited ``emcee`` pilot support for three-stage posteriors."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable

import emcee
import numpy as np
from emcee.state import State

from .mcmc_three_stage_artifacts import (
    canonical_json_sha256,
    completed_backend_guard,
    immutable_checkpoint_snapshot,
    sha256_file,
    write_json_exclusive,
)
from .mcmc_three_stage_posterior import SamplingPosteriorResult, ThreeStagePosterior
from .mcmc_three_stage_sampler_geometry import CoordinateSaturation


REASON_CODES = {
    None: 0,
    "outside_prior_support": 1,
    "nonpositive_or_nonfinite_cn_prediction": 2,
    "nonfinite_gpp_prediction": 3,
    "nonfinite_sr_prediction": 4,
    "coordinate_saturation": 5,
}

BLOB_DTYPE = np.dtype([
    ("log_physical_posterior", "f8"),
    ("log_prior", "f8"),
    ("log_likelihood_gpp", "f8"),
    ("log_likelihood_sr", "f8"),
    ("log_likelihood_cn", "f8"),
    ("log_abs_det_jacobian", "f8"),
    ("reason_code", "i2"),
])


def _json_float(value: float) -> float | str:
    number = float(value)
    if np.isneginf(number):
        return "-Infinity"
    if np.isposinf(number):
        return "Infinity"
    if np.isnan(number):
        raise ValueError("NaN is prohibited in the proposal ledger")
    return number


def random_state_equal(first: Any, second: Any) -> bool:
    sequence_types = (list, tuple)
    if (not isinstance(first, sequence_types) or not isinstance(second, sequence_types)
            or len(first) != len(second)):
        return False
    for left, right in zip(first, second):
        if isinstance(left, np.ndarray) or isinstance(right, np.ndarray):
            if not np.array_equal(np.asarray(left), np.asarray(right)):
                return False
        elif left != right:
            return False
    return True


def result_blob(result: SamplingPosteriorResult) -> tuple[float, float, float, float, float, float, int]:
    physical = result.physical
    if physical.evaluation_error not in REASON_CODES:
        raise RuntimeError(f"unregistered numerical rejection reason: {physical.evaluation_error}")
    return (
        float(physical.log_posterior),
        float(physical.log_prior),
        float(physical.log_likelihood_gpp),
        float(physical.log_likelihood_sr),
        float(physical.log_likelihood_cn),
        float(result.log_abs_det_jacobian),
        REASON_CODES[physical.evaluation_error],
    )


class ThreeStageSamplingTarget:
    """Vectorized emcee target returning fixed-schema component blobs."""

    def __init__(self, posterior: ThreeStagePosterior) -> None:
        self.posterior = posterior

    def __call__(self, coordinates: np.ndarray) -> list[tuple[Any, ...]]:
        results = self.posterior.evaluate_sampling_batch(coordinates)
        return [(float(result.log_sampling_posterior), *result_blob(result)) for result in results]


class ProposalAuditLedger:
    """Durable append-only JSONL ledger for every evaluated proposal."""

    def __init__(
        self, path: Path | str, *, sampler_to_physical: Callable[[np.ndarray], np.ndarray],
        resume: bool = False, strict_mapping_errors: bool = False,
    ) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists() and not resume:
            raise FileExistsError(f"proposal ledger already exists: {self.path}")
        if not self.path.exists() and resume:
            raise FileNotFoundError(f"proposal ledger missing for resume: {self.path}")
        self._sampler_to_physical = sampler_to_physical
        self.strict_mapping_errors = strict_mapping_errors
        self.current_step = 0
        self.proposal_call = 0
        if resume:
            with self.path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    if line.strip():
                        self.proposal_call = max(
                            self.proposal_call,
                            int(json.loads(line)["proposal_call"]),
                        )

    def record(
        self, *, move: str, walker_indices: np.ndarray, sampler_coordinates: np.ndarray,
        log_probabilities: np.ndarray, blobs: np.ndarray | None, accepted: np.ndarray,
    ) -> None:
        self.proposal_call += 1
        physical: list[list[float] | None] = []
        for row in np.asarray(sampler_coordinates, dtype=np.float64):
            try:
                mapped = np.asarray(self._sampler_to_physical(row), dtype=np.float64)
            except CoordinateSaturation:
                physical.append(None)
            except (ValueError, FloatingPointError):
                if self.strict_mapping_errors:
                    raise
                physical.append(None)
            else:
                physical.append(mapped.tolist())
        rows = []
        for local, walker in enumerate(np.asarray(walker_indices, dtype=np.int64)):
            blob_payload = None
            if blobs is not None:
                value = blobs[local]
                blob_payload = {
                    name: (int(value[name]) if name == "reason_code" else _json_float(value[name]))
                    for name in BLOB_DTYPE.names or ()
                }
            rows.append({
                "schema": "mcmc-three-stage-proposal-v1",
                "step": int(self.current_step),
                "proposal_call": int(self.proposal_call),
                "move": move,
                "walker": int(walker),
                "sampler_coordinates": np.asarray(sampler_coordinates[local], dtype=float).tolist(),
                "physical_parameters": physical[local],
                "log_sampling_posterior": _json_float(log_probabilities[local]),
                "blob": blob_payload,
                "accepted": bool(accepted[walker]),
            })
        descriptor = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        with os.fdopen(descriptor, "a", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())


class _AuditedRedBlueMixin:
    audit_ledger: ProposalAuditLedger
    audit_move_name: str

    def propose(self, model, state):  # type: ignore[no-untyped-def]
        nwalkers, ndim = state.coords.shape
        if nwalkers < 2 * ndim and not self.live_dangerously:
            raise RuntimeError(
                "It is unadvisable to use a red-blue move with fewer walkers than twice the dimensions"
            )
        self.setup(state.coords)
        accepted = np.zeros(nwalkers, dtype=bool)
        all_inds = np.arange(nwalkers)
        inds = all_inds % self.nsplits
        if self.randomize_split:
            model.random.shuffle(inds)
        for split in range(self.nsplits):
            subset = inds == split
            sets = [state.coords[inds == value] for value in range(self.nsplits)]
            sample = sets[split]
            complement = sets[:split] + sets[split + 1 :]
            proposal, factors = self.get_proposal(sample, complement, model.random)
            new_log_probs, new_blobs = model.compute_log_prob_fn(proposal)
            for walker, factor, new_log_prob in zip(all_inds[subset], factors, new_log_probs):
                difference = factor + new_log_prob - state.log_prob[walker]
                if difference > np.log(model.random.rand()):
                    accepted[walker] = True
            self.audit_ledger.record(
                move=self.audit_move_name,
                walker_indices=all_inds[subset],
                sampler_coordinates=proposal,
                log_probabilities=new_log_probs,
                blobs=new_blobs,
                accepted=accepted,
            )
            new_state = State(proposal, log_prob=new_log_probs, blobs=new_blobs)
            state = self.update(state, new_state, accepted, subset)
        return state, accepted


class AuditedDEMove(_AuditedRedBlueMixin, emcee.moves.DEMove):
    def __init__(self, ledger: ProposalAuditLedger) -> None:
        self.audit_ledger = ledger
        self.audit_move_name = "DEMove"
        super().__init__(sigma=1.0e-5, gamma0=None)


class AuditedDESnookerMove(_AuditedRedBlueMixin, emcee.moves.DESnookerMove):
    def __init__(self, ledger: ProposalAuditLedger) -> None:
        self.audit_ledger = ledger
        self.audit_move_name = "DESnookerMove"
        super().__init__(gammas=1.7)


def sampler_identity(payload: dict[str, Any]) -> tuple[dict[str, Any], str]:
    required = {
        "site", "prior_id", "parameter_names", "posterior_target_sha256", "pool_sha256",
        "walker_sha256", "emcee_version", "move_configuration", "seed", "nwalkers", "ndim",
    }
    missing = sorted(required - set(payload))
    if missing:
        raise ValueError(f"sampler identity missing fields: {missing}")
    normalized = dict(payload)
    if "coordinate_system_id" in normalized:
        new_required = {
            "geometry_source_sha256", "sampler_source_sha256", "posterior_source_sha256",
            "execution_checksum_manifest_sha256", "release_manifest_sha256",
            "walker_coordinates_sha256",
        }
        absent = sorted(new_required - set(normalized))
        if absent:
            raise ValueError(f"new sampler identity missing fields: {absent}")
        normalized["schema"] = "mcmc-three-stage-sampler-identity-v2"
    else:
        normalized["schema"] = "mcmc-three-stage-sampler-identity-v1"
    return normalized, canonical_json_sha256(normalized)


def _load_or_create_identity(run_root: Path, payload: dict[str, Any], *, resume: bool) -> str:
    normalized, digest = sampler_identity(payload)
    path = run_root / "identity.json"
    if resume:
        if not path.is_file() or json.loads(path.read_text(encoding="utf-8")) != normalized:
            raise ValueError("sampler resume identity mismatch")
    else:
        write_json_exclusive(path, normalized)
    return digest


def run_sampler_block(
    *, posterior: ThreeStagePosterior, initial_sampler_coordinates: np.ndarray,
    run_directory: Path | str, identity: dict[str, Any], target_iteration: int,
    checkpoint_interval: int = 64, resume: bool = False,
) -> dict[str, Any]:
    """Run or resume to an exact iteration without marking the run complete."""

    root = Path(run_directory)
    if root.exists():
        if not root.is_dir() or (not resume and any(root.iterdir())):
            raise FileExistsError(f"sampler run directory is not empty: {root}")
    else:
        root.mkdir(parents=True)
    completed_backend_guard(root)
    coordinate_id = getattr(posterior, "sampling_coordinate_system", "legacy_three_stage_v1")
    if coordinate_id == "ppe1_prior_unit_logit_v1":
        if identity.get("coordinate_system_id") != coordinate_id:
            raise ValueError("new coordinate system requires exact sampler identity")
    elif "coordinate_system_id" in identity:
        raise ValueError("sampler coordinate identity does not match posterior")
    identity_sha = _load_or_create_identity(root, identity, resume=resume)
    backend_path = root / "active_backend.h5"
    ledger = ProposalAuditLedger(
        root / "proposal_ledger.jsonl",
        sampler_to_physical=getattr(
            posterior, "sampling_geometry", posterior.prior.coordinate_transform
        ).sampler_to_physical,
        resume=resume,
        strict_mapping_errors=coordinate_id == "ppe1_prior_unit_logit_v1",
    )
    nwalkers = int(identity["nwalkers"])
    ndim = int(identity["ndim"])
    initial = np.asarray(initial_sampler_coordinates, dtype=np.float64)
    if initial.shape != (nwalkers, ndim) or not np.all(np.isfinite(initial)):
        raise ValueError("initial sampler coordinates do not match locked walker geometry")
    if resume:
        if not backend_path.is_file():
            raise FileNotFoundError(f"sampler backend missing for resume: {backend_path}")
        backend = emcee.backends.HDFBackend(str(backend_path))
        if int(backend.iteration) <= 0 or int(backend.iteration) >= target_iteration:
            raise ValueError("resume backend iteration is not eligible for requested target")
        start_state = None
    else:
        if backend_path.exists():
            raise FileExistsError(f"sampler backend already exists: {backend_path}")
        backend = emcee.backends.HDFBackend(str(backend_path))
        backend.reset(nwalkers, ndim)
        start_state = initial
    target = ThreeStageSamplingTarget(posterior)
    moves = [(AuditedDEMove(ledger), 0.80), (AuditedDESnookerMove(ledger), 0.20)]
    sampler = emcee.EnsembleSampler(
        nwalkers, ndim, target, moves=moves, backend=backend, vectorize=True,
        blobs_dtype=BLOB_DTYPE,
    )
    if not resume:
        random = np.random.RandomState(int(identity["seed"]))
        sampler.random_state = random.get_state()
    while int(sampler.iteration) < int(target_iteration):
        ledger.current_step = int(sampler.iteration) + 1
        sampler.run_mcmc(start_state if int(sampler.iteration) == 0 else None, 1, progress=False)
        start_state = None
        if int(sampler.iteration) % int(checkpoint_interval) == 0:
            immutable_checkpoint_snapshot(
                backend_path=backend_path,
                checkpoint_root=root / "checkpoints",
                step=int(sampler.iteration),
                identity_sha256=identity_sha,
            )
    return {
        "schema": "mcmc-three-stage-sampler-block-v1",
        "identity_sha256": identity_sha,
        "iteration": int(sampler.iteration),
        "backend_sha256": sha256_file(backend_path),
        "proposal_ledger_sha256": sha256_file(ledger.path),
        "acceptance_fraction": np.asarray(sampler.acceptance_fraction, dtype=float).tolist(),
    }


def finalize_sampler_run(run_directory: Path | str, *, decision: str) -> dict[str, Any]:
    root = Path(run_directory)
    completed_backend_guard(root)
    backend = root / "active_backend.h5"
    identity = root / "identity.json"
    ledger = root / "proposal_ledger.jsonl"
    if not backend.is_file() or not identity.is_file() or not ledger.is_file():
        raise ValueError("sampler run is incomplete and cannot be finalized")
    payload = {
        "schema": "mcmc-three-stage-completed-run-v1",
        "decision": str(decision),
        "identity_sha256": sha256_file(identity),
        "backend_sha256": sha256_file(backend),
        "proposal_ledger_sha256": sha256_file(ledger),
    }
    write_json_exclusive(root / "COMPLETED.json", payload)
    backend.chmod(0o444)
    ledger.chmod(0o444)
    identity.chmod(0o444)
    return payload
