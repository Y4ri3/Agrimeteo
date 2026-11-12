"""Profils de culture : lus dans les fichiers YAML du module ml (RULES_DIR)."""

from __future__ import annotations

from functools import lru_cache

from agrimeteo_ml import Profile, load_profiles

from app.core import config
from app.schemas.predictions import Crop


@lru_cache
def _profiles(directory: str) -> dict[str, Profile]:
    return load_profiles(directory)


def profile(crop_id: str) -> Profile | None:
    return _profiles(config.RULES_DIR).get(crop_id)


def _crop(p: Profile) -> Crop:
    return Crop(
        id=p.id, label=p.label, rule_profile_version=p.version, rule_status=p.status, zones=p.zones or None
    )


def all_crops() -> list[Crop]:
    return [_crop(p) for p in _profiles(config.RULES_DIR).values()]


def find(crop_id: str) -> Crop | None:
    p = profile(crop_id)
    return _crop(p) if p else None
