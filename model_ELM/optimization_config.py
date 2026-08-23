"""Validation for the immutable three-stage coupled-optimization YAML contract."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


REQUIRED_SECTIONS = ("shared", "initialization", "optimization", "reporting")


def _json_value(value: Any) -> Any:
    """Convert common scientific values to portable JSON manifest values."""
    if isinstance(value, Path):
        return str(value)
    if hasattr(value, "tolist"):
        return value.tolist()
    if hasattr(value, "item"):
        return value.item()
    raise TypeError(f"cannot serialize {type(value).__name__} in a stage manifest")


def load_campaign(path: str | Path, stage: str) -> dict[str, Any]:
    """Load one campaign YAML and return the shared plus stage-specific mapping."""
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - verified in Puma preflight
        raise RuntimeError("PyYAML is required for coupled optimization campaign files") from exc
    source = Path(path)
    data = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(data, Mapping):
        raise ValueError("campaign YAML must contain a mapping")
    missing = [name for name in REQUIRED_SECTIONS if not isinstance(data.get(name), Mapping)]
    if missing:
        raise ValueError(f"campaign YAML missing mapping sections: {', '.join(missing)}")
    if stage not in REQUIRED_SECTIONS[1:]:
        raise ValueError(f"unsupported campaign stage: {stage}")
    shared, stage_values = dict(data["shared"]), dict(data[stage])
    result = {"campaign_path": str(source.resolve()), "campaign_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "stage": stage, "shared": shared, stage: stage_values}
    if not shared.get("sites") or not isinstance(shared["sites"], list):
        raise ValueError("shared.sites must be a non-empty list")
    return result


def write_stage_manifest(root: str | Path, payload: Mapping[str, Any]) -> Path:
    """Write a deterministic, non-overwriting stage receipt."""
    destination = Path(root) / "stage_manifest.json"
    if destination.exists():
        raise FileExistsError(f"refusing to overwrite stage manifest: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(dict(payload), default=_json_value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return destination
