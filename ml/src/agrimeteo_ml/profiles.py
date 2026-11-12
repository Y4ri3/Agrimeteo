"""Profils de culture : fichiers YAML versionnés, validés à la lecture (critère P-06)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

STATUSES = ("a_valider", "valide_par_source")
DIRECTIONS = ("lower_is_worse", "higher_is_worse")  # sens dans lequel la valeur devient défavorable


@dataclass(frozen=True)
class Criterion:
    id: str
    label: str
    indicator: str  # nom dans agrimeteo_ml.indicators.INDICATORS
    window_days: int  # fenêtre (derniers jours) sur laquelle l'indicateur est calculé
    unit: str
    direction: str
    blocking: bool
    vigilance: float | None  # un seuil peut être absent ; les deux absents = « seuil non défini »
    unfavorable: float | None
    source: str | None


@dataclass(frozen=True)
class Profile:
    id: str
    label: str
    version: str
    status: str
    zones: str
    window_days: int
    criteria: tuple[Criterion, ...]
    limits: tuple[str, ...]


def problems(data: dict[str, Any]) -> list[str]:
    """Liste lisible des défauts d'un profil (vide = profil valide)."""
    from agrimeteo_ml.indicators import INDICATORS

    out: list[str] = []
    for key in ("id", "label", "version", "status", "criteria"):
        if not data.get(key):
            out.append(f"champ manquant : {key}")
    if data.get("status") not in STATUSES:
        out.append(f"status invalide : {data.get('status')!r} (attendu : {', '.join(STATUSES)})")
    for c in data.get("criteria") or []:
        cid = c.get("id", "?")
        th = c.get("thresholds") or {}
        vig, unf = th.get("vigilance"), th.get("unfavorable")
        if c.get("indicator") not in INDICATORS:
            out.append(f"{cid} : indicateur inconnu {c.get('indicator')!r}")
        if c.get("direction") not in DIRECTIONS:
            out.append(f"{cid} : direction invalide")
        if vig is not None and unf is not None:
            ordered = unf <= vig if c.get("direction") == "lower_is_worse" else vig <= unf
            if not ordered:
                out.append(f"{cid} : seuils incohérents avec la direction {c.get('direction')}")
        if (vig is not None or unf is not None) and not c.get("source"):
            out.append(f"{cid} : seuil sans source (P-06)")
        if data.get("status") == "valide_par_source" and (
            (vig is None and unf is None) or not c.get("source")
        ):
            out.append(f"{cid} : profil 'valide_par_source' exige seuils et source")
    return out


def load_profile(path: str | Path) -> Profile:
    path = Path(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    found = problems(data)
    if found:
        raise ValueError(f"{path.name} : " + " ; ".join(found))
    return Profile(
        id=data["id"],
        label=data["label"],
        version=str(data["version"]),
        status=data["status"],
        zones=str(data.get("zones") or ""),
        window_days=int((data.get("analysis") or {}).get("window_days", 30)),
        criteria=tuple(
            Criterion(
                id=c["id"],
                label=c.get("label", c["id"]),
                indicator=c["indicator"],
                window_days=int(c.get("window_days") or (data.get("analysis") or {}).get("window_days", 30)),
                unit=c.get("unit", ""),
                direction=c["direction"],
                blocking=bool(c.get("blocking", False)),
                vigilance=(c.get("thresholds") or {}).get("vigilance"),
                unfavorable=(c.get("thresholds") or {}).get("unfavorable"),
                source=c.get("source"),
            )
            for c in data["criteria"]
        ),
        limits=tuple(data.get("limits") or ()),
    )


def load_profiles(directory: str | Path) -> dict[str, Profile]:
    return {p.id: p for p in (load_profile(f) for f in sorted(Path(directory).glob("*.yaml")))}
