"""Contrôle des dates d'entrée, commun aux endpoints (A-03)."""

from __future__ import annotations

from datetime import date, timedelta

from app.core import config
from app.core.errors import AppError

EARLIEST = date(1940, 1, 1)  # début de la réanalyse ERA5 utilisée par Open-Meteo


def check_period(start: date, end: date) -> None:
    if start > end:
        raise AppError(
            422,
            "VALIDATION_ERROR",
            "Vérifiez les coordonnées et les dates saisies.",
            [{"field": "start_date"}],
        )
    if (end - start).days + 1 > config.MAX_PERIOD_DAYS:
        raise AppError(
            422,
            "PERIOD_TOO_LONG",
            "La période demandée dépasse la durée maximale autorisée.",
            [{"field": "end_date", "max_period_days": config.MAX_PERIOD_DAYS}],
        )
    if start < EARLIEST or end > date.today():
        raise AppError(
            422, "DATE_OUT_OF_RANGE", "Aucune donnée disponible pour cette date.", [{"field": "end_date"}]
        )


def default_reference_date() -> date:
    return date.today() - timedelta(days=2)  # les archives sont publiées avec quelques jours de retard
