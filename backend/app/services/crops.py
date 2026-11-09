"""Profils de culture. PROVISOIRE : le lot 2 fournira le chargeur des profils YAML (ml/rules/)."""

from __future__ import annotations

from app.schemas.predictions import Crop

CROPS = [
    Crop(
        id="culture_exemple_a",
        label="Culture exemple A (profil de démonstration)",
        rule_profile_version="0.1.0",
        rule_status="a_valider",
    ),
]


def find(crop_id: str) -> Crop | None:
    return next((c for c in CROPS if c.id == crop_id), None)
