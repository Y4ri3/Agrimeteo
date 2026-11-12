"""Format d'erreur commun : {"error": {"code", "message", "details"}, "request_id"}."""

from __future__ import annotations

from typing import Any


class AppError(Exception):
    def __init__(self, status: int, code: str, message: str, details: list[dict[str, Any]] | None = None):
        self.status = status
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)


class ProviderUnavailable(AppError):
    def __init__(self) -> None:
        super().__init__(502, "PROVIDER_UNAVAILABLE", "Le service de données météo est indisponible.")


class ProviderRateLimited(AppError):
    def __init__(self) -> None:
        super().__init__(503, "PROVIDER_RATE_LIMITED", "Trop de demandes : réessayez dans un instant.")


class ProviderTimeout(AppError):
    def __init__(self) -> None:
        super().__init__(504, "PROVIDER_TIMEOUT", "Le service de données ne répond pas.")
