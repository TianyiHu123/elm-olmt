"""Integrated physical and sampling-coordinate three-stage posterior APIs."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import time as timing
from typing import Sequence

import numpy as np
from netCDF4 import Dataset

from .mcmc_prior import PPE1, Prior18
from .mcmc_three_stage_likelihood import gaussian_log_likelihood, joint_cn_log_likelihood
from .mcmc_three_stage_observations import (
    ObservationReleaseConfig,
    ThreeStageObservationContext,
    load_three_stage_observations,
)
from .mcmc_three_stage_release import (
    LoadedThreeStageRelease,
    ThreeStageReleaseConfig,
    load_three_stage_release,
)
from .three_stage_gpp import FORCING_NAMES


@dataclass(frozen=True)
class PosteriorResult:
    site: str
    prior_id: str
    gpp_resolution: str
    sr_resolution: str
    cn_observation_cv: float
    include_cn: bool
    log_prior: float
    log_likelihood_gpp: float
    log_likelihood_sr: float
    log_likelihood_cn: float
    log_posterior: float
    n_gpp: int
    n_sr: int
    surrogate_evaluated: bool
    gpp_raw_min: float | None
    evaluation_error: str | None
    provenance: dict[str, object]


@dataclass(frozen=True)
class SamplingPosteriorResult:
    physical: PosteriorResult
    log_abs_det_jacobian: float
    log_sampling_posterior: float


class ThreeStagePosterior:
    def __init__(
        self,
        *,
        site: str,
        prior: Prior18,
        release: LoadedThreeStageRelease,
        observations: ThreeStageObservationContext,
        gpp_resolution: str,
        sr_resolution: str,
        cn_observation_cv: float,
        include_cn: bool,
        start: int = 720,
        end: int | None = None,
        member_chunk: int = 16,
    ) -> None:
        if site not in release.config.sites or observations.site != site:
            raise ValueError("posterior site identity mismatch")
        if prior.prior_id != PPE1 or release.config.prior_id != prior.prior_id:
            raise ValueError("posterior prior/release incompatibility")
        if gpp_resolution not in ("hourly", "daily") or sr_resolution not in ("hourly", "daily"):
            raise ValueError("posterior flux resolution must be hourly or daily")
        cv = float(cn_observation_cv)
        if cv not in observations.soil_cn.covariance_by_cv:
            raise ValueError("unsupported C/N observational CV")
        actual_end = observations.forcing_hours if end is None else int(end)
        if int(start) < 720 or actual_end <= int(start) or actual_end > observations.forcing_hours:
            raise ValueError("invalid posterior forcing window")
        if member_chunk <= 0:
            raise ValueError("member_chunk must be positive")
        self.site = site
        self.prior = prior
        self.release = release
        self.observations = observations
        self.gpp_resolution = gpp_resolution
        self.sr_resolution = sr_resolution
        self.cn_observation_cv = cv
        self.include_cn = bool(include_cn)
        self.start = int(start)
        self.end = actual_end
        self.member_chunk = int(member_chunk)
        self.gpp_operator = observations.operator("GPP", gpp_resolution).window(self.start, self.end)
        self.sr_operator = observations.operator("SR", sr_resolution).window(self.start, self.end)
        snapshot_root = Path(release.config.snapshot_root)
        with Dataset(str(snapshot_root / "sites" / site / "input_data_v1.nc"), "r") as dataset:
            self.forcing = {
                name: np.asarray(dataset.variables[name][:self.end], dtype=np.float64)
                for name in FORCING_NAMES
            }
            self.time = np.asarray(dataset.variables["time"][:self.end], dtype=np.int64)
        if not np.array_equal(self.time, np.arange(self.end, dtype=np.int64)):
            raise ValueError("posterior forcing time axis mismatch")

    def _invalid_result(self, log_prior: float) -> PosteriorResult:
        return PosteriorResult(
            site=self.site,
            prior_id=self.prior.prior_id,
            gpp_resolution=self.gpp_resolution,
            sr_resolution=self.sr_resolution,
            cn_observation_cv=self.cn_observation_cv,
            include_cn=self.include_cn,
            log_prior=float(log_prior),
            log_likelihood_gpp=0.0,
            log_likelihood_sr=0.0,
            log_likelihood_cn=0.0,
            log_posterior=float("-inf"),
            n_gpp=self.gpp_operator.count,
            n_sr=self.sr_operator.count,
            surrogate_evaluated=False,
            gpp_raw_min=None,
            evaluation_error="outside_prior_support",
            provenance=self._provenance(),
        )

    def _provenance(self) -> dict[str, object]:
        return {
            "release_id": self.release.config.release_id,
            "release_manifest_sha256": self.release.config.release_manifest_sha256,
            "snapshot_sha256": self.release.config.snapshot_sha256,
            "uncertainty_handoff_sha256": self.release.config.uncertainty_handoff_sha256,
            "uncertainty_manifest_sha256": self.release.config.uncertainty_manifest_sha256,
            "uncertainty_validation_sha256": self.release.config.uncertainty_validation_sha256,
            "observation_catalog_sha256": self.observations.release_catalog_sha256,
            "observation_manifest_sha256": self.observations.release_manifest_sha256,
            "observation_validation_sha256": self.observations.validation_report_sha256,
            "site_uncertainty_product_sha256": self.observations.uncertainty_product_sha256,
            "site_soil_product_sha256": self.observations.soil_product_sha256,
            "site_depth_source_sha256": self.observations.depth_source_sha256,
            "start": self.start,
            "end": self.end,
            "gpp_output_policy": "hard_zero_v1",
            "contains_elm_truth": False,
            "fixed_test_access_for_uncertainty": False,
        }

    def evaluate(self, theta: Sequence[float] | np.ndarray) -> PosteriorResult:
        values = np.asarray(theta, dtype=np.float64)
        if values.shape != (18,):
            raise ValueError("posterior parameter vector must have shape (18,)")
        return self.evaluate_batch(values.reshape(1, 18))[0]

    def evaluate_batch(self, theta: Sequence[Sequence[float]] | np.ndarray) -> list[PosteriorResult]:
        results, _ = self.evaluate_batch_timed(theta)
        return results

    def evaluate_batch_timed(
        self, theta: Sequence[Sequence[float]] | np.ndarray,
    ) -> tuple[list[PosteriorResult], dict[str, float]]:
        total_started = timing.perf_counter()
        matrix = np.asarray(theta, dtype=np.float64)
        if matrix.ndim != 2 or matrix.shape[1] != 18:
            raise ValueError("posterior parameter batch must have shape (n,18)")
        if matrix.shape[0] == 0:
            raise ValueError("posterior parameter batch must not be empty")
        prior_started = timing.perf_counter()
        log_prior = np.asarray(self.prior.log_density(matrix), dtype=np.float64)
        prior_seconds = timing.perf_counter() - prior_started
        valid = np.isfinite(log_prior)
        results: list[PosteriorResult | None] = [None] * matrix.shape[0]
        for index in np.flatnonzero(~valid):
            results[int(index)] = self._invalid_result(float(log_prior[index]))
        surrogate_seconds = 0.0
        likelihood_seconds = 0.0
        if np.any(valid):
            selected_indices = np.flatnonzero(valid)
            surrogate_started = timing.perf_counter()
            inference = self.release.engine.predict(
                matrix[valid], site=self.site, forcing=self.forcing, time=self.time,
                start=self.start, end=self.end, member_chunk=self.member_chunk,
            )
            surrogate_seconds = timing.perf_counter() - surrogate_started
            if inference.provenance.get("contains_elm_truth") is not False:
                raise ValueError("three-stage inference provenance indicates target leakage")
            likelihood_started = timing.perf_counter()
            for local, original in enumerate(selected_indices):
                full_stocks = np.asarray([inference.totsomc[local], inference.totsomn[local]], dtype=np.float64)
                gpp_prediction = self.gpp_operator.aggregate_predictions(inference.gpp[local], self.start)
                sr_prediction = self.sr_operator.aggregate_predictions(inference.sr[local], self.start)
                ll_gpp = gaussian_log_likelihood(
                    self.gpp_operator.observed, gpp_prediction,
                    self.gpp_operator.observation_sigma, self.gpp_operator.surrogate_rmse,
                )
                ll_sr = gaussian_log_likelihood(
                    self.sr_operator.observed, sr_prediction,
                    self.sr_operator.observation_sigma, self.sr_operator.surrogate_rmse,
                )
                ll_cn = 0.0
                evaluation_error = None
                if self.include_cn:
                    soil = self.observations.soil_cn
                    if not np.all(np.isfinite(full_stocks)) or np.any(full_stocks <= 0.0):
                        ll_cn = float("-inf")
                        evaluation_error = "nonpositive_or_nonfinite_cn_prediction"
                    else:
                        ll_cn = joint_cn_log_likelihood(
                            soil.observed_stocks, full_stocks, soil.depth_fraction,
                            soil.total_bias_correction, soil.covariance_by_cv[self.cn_observation_cv],
                        )
                total = float(log_prior[original] + ll_gpp + ll_sr + ll_cn)
                results[int(original)] = PosteriorResult(
                    site=self.site,
                    prior_id=self.prior.prior_id,
                    gpp_resolution=self.gpp_resolution,
                    sr_resolution=self.sr_resolution,
                    cn_observation_cv=self.cn_observation_cv,
                    include_cn=self.include_cn,
                    log_prior=float(log_prior[original]),
                    log_likelihood_gpp=ll_gpp,
                    log_likelihood_sr=ll_sr,
                    log_likelihood_cn=ll_cn,
                    log_posterior=total,
                    n_gpp=self.gpp_operator.count,
                    n_sr=self.sr_operator.count,
                    surrogate_evaluated=True,
                    gpp_raw_min=float(np.min(inference.gpp_raw[local])),
                    evaluation_error=evaluation_error,
                    provenance=self._provenance(),
                )
            likelihood_seconds = timing.perf_counter() - likelihood_started
        if any(result is None for result in results):
            raise RuntimeError("posterior batch result ordering was not completely populated")
        ordered = [results[index] for index in range(len(results))]
        return ordered, {
            "prior_seconds": prior_seconds,
            "surrogate_seconds": surrogate_seconds,
            "alignment_likelihood_seconds": likelihood_seconds,
            "total_seconds": timing.perf_counter() - total_started,
        }

    def evaluate_sampling(self, sampler_theta: Sequence[float] | np.ndarray) -> SamplingPosteriorResult:
        sampler = np.asarray(sampler_theta, dtype=np.float64)
        if sampler.shape != (18,):
            raise ValueError("sampler parameter vector must have shape (18,)")
        physical_theta = self.prior.coordinate_transform.sampler_to_physical(sampler)
        physical = self.evaluate(physical_theta)
        jacobian = float(self.prior.coordinate_transform.log_abs_det_dphysical_dsampler(sampler))
        return SamplingPosteriorResult(
            physical=physical,
            log_abs_det_jacobian=jacobian,
            log_sampling_posterior=float(physical.log_posterior + jacobian),
        )


def load_three_stage_posterior(
    *,
    site: str,
    prior_id: str,
    prior_root: Path | str,
    surrogate_release: ThreeStageReleaseConfig,
    observation_release: ObservationReleaseConfig,
    gpp_resolution: str = "daily",
    sr_resolution: str = "daily",
    cn_observation_cv: float = 0.30,
    include_cn: bool = True,
    start: int = 720,
    end: int | None = None,
    member_chunk: int = 16,
) -> ThreeStagePosterior:
    prior = Prior18.from_directory(prior_id, prior_root)
    release = load_three_stage_release(prior=prior, config=surrogate_release)
    observations = load_three_stage_observations(site=site, config=observation_release)
    return ThreeStagePosterior(
        site=site,
        prior=prior,
        release=release,
        observations=observations,
        gpp_resolution=gpp_resolution,
        sr_resolution=sr_resolution,
        cn_observation_cv=cn_observation_cv,
        include_cn=include_cn,
        start=start,
        end=end,
        member_chunk=member_chunk,
    )
