"""General public loader for validated three-stage MCMC surrogate releases.

The public API is configuration driven and does not encode a PPE identity in
its name.  Iter003 deliberately supports only the existing validated PPE1
release and delegates to its proven loader after checking the explicit
configuration.  This is a compatibility layer, not a speculative artifact
framework.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .mcmc_coupled_adapter import (
    CONSUMED_RELEASE_FILES,
    EXPECTED_CATALOG_SHA256,
    EXPECTED_RELEASE_MANIFEST_SHA256,
    EXPECTED_SNAPSHOT_SHA256,
    LoadedCoupledRelease,
    load_ppe1_coupled_release,
)
from .mcmc_prior import PPE1, Prior18


CONFIG_SCHEMA = "mcmc-three-stage-release-config-v1"
IMPLEMENTATION_ID = "validated-coupled-release-v1"


@dataclass(frozen=True)
class ThreeStageReleaseConfig:
    schema: str
    implementation_id: str
    prior_id: str
    release_id: str
    release_root: Path
    snapshot_root: Path
    uncertainty_root: Path
    uncertainty_handoff_sha256: str
    uncertainty_manifest_sha256: str
    uncertainty_validation_sha256: str
    source_file: Path
    release_manifest_sha256: str
    catalog_sha256: str
    snapshot_sha256: str
    sites: tuple[str, ...] = ("ABBY", "JERC")

    def validate(self) -> None:
        if self.schema != CONFIG_SCHEMA:
            raise ValueError(f"unsupported three-stage release config schema: {self.schema}")
        if self.implementation_id != IMPLEMENTATION_ID:
            raise ValueError(f"unsupported three-stage implementation: {self.implementation_id}")
        if self.prior_id != PPE1:
            raise ValueError("the current validated three-stage release supports prior_id=ppe1 only")
        if self.release_id != "release_0001":
            raise ValueError(f"unsupported three-stage release: {self.release_id}")
        if self.sites != ("ABBY", "JERC"):
            raise ValueError("three-stage release site identity mismatch")
        expected = (
            (self.release_manifest_sha256, EXPECTED_RELEASE_MANIFEST_SHA256, "release manifest"),
            (self.catalog_sha256, EXPECTED_CATALOG_SHA256, "catalog"),
            (self.snapshot_sha256, EXPECTED_SNAPSHOT_SHA256, "snapshot"),
            (self.uncertainty_handoff_sha256,
             CONSUMED_RELEASE_FILES["uncertainty/uncertainty_handoff.json"][1],
             "uncertainty handoff"),
            (self.uncertainty_manifest_sha256,
             CONSUMED_RELEASE_FILES["uncertainty/products_manifest.json"][1],
             "uncertainty manifest"),
            (self.uncertainty_validation_sha256,
             CONSUMED_RELEASE_FILES["uncertainty/final_validation_report.json"][1],
             "uncertainty validation"),
        )
        for observed, locked, label in expected:
            if observed != locked:
                raise ValueError(f"three-stage {label} configured identity mismatch")
        for value, label in (
            (self.release_root, "release root"),
            (self.snapshot_root, "snapshot root"),
            (self.uncertainty_root, "uncertainty root"),
        ):
            if not Path(value).expanduser().resolve().is_dir():
                raise ValueError(f"missing three-stage {label}: {value}")
        if not Path(self.source_file).expanduser().resolve().is_file():
            raise ValueError(f"missing three-stage source file: {self.source_file}")


@dataclass(frozen=True)
class LoadedThreeStageRelease:
    engine: Any
    config: ThreeStageReleaseConfig
    compatibility_layer: str
    validated_release: LoadedCoupledRelease

    @property
    def loading_seconds(self) -> dict[str, float]:
        return dict(self.validated_release.loading_seconds)


def load_three_stage_release(*, prior: Prior18, config: ThreeStageReleaseConfig) -> LoadedThreeStageRelease:
    """Load the configured validated release or fail before inference."""

    config.validate()
    if prior.prior_id != config.prior_id:
        raise ValueError(
            f"prior/release incompatibility: prior_id={prior.prior_id}, configured={config.prior_id}"
        )
    loaded = load_ppe1_coupled_release(
        prior=prior,
        release_root=config.release_root,
        snapshot_root=config.snapshot_root,
        source_file=config.source_file,
        uncertainty_root=config.uncertainty_root,
    )
    return LoadedThreeStageRelease(
        engine=loaded.engine,
        config=config,
        compatibility_layer="load_ppe1_coupled_release",
        validated_release=loaded,
    )
