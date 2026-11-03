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
