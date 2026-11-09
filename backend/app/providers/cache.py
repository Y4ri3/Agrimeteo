"""Cache de fichiers JSON devant un fournisseur (D-06). Une panne du cache ne casse jamais une requête."""

from __future__ import annotations

import hashlib
import json
import logging
import time
from datetime import date
from pathlib import Path

from app.core import config
from app.providers.base import WeatherProvider
from app.schemas.weather import DailyRecord

log = logging.getLogger("agrimeteo.cache")


class CachedProvider:
    def __init__(self, inner: WeatherProvider, directory: str | None = None, ttl_hours: int | None = None):
        self.inner = inner
        self.id = inner.id
        self.source = inner.source
        self._dir = Path(directory or config.CACHE_DIR)
        self._ttl = (config.CACHE_TTL_HOURS if ttl_hours is None else ttl_hours) * 3600

    def _path(self, latitude: float, longitude: float, start: date, end: date) -> Path:
        key = f"{self.id}|{latitude:.4f}|{longitude:.4f}|{start}|{end}"
        return self._dir / f"{hashlib.sha256(key.encode()).hexdigest()}.json"

    def daily(self, latitude: float, longitude: float, start: date, end: date) -> list[DailyRecord]:
        path = self._path(latitude, longitude, start, end)
        try:
            if path.exists() and time.time() - path.stat().st_mtime < self._ttl:
                return [DailyRecord(**r) for r in json.loads(path.read_text(encoding="utf-8"))]
        except (OSError, ValueError, TypeError):
            log.warning("cache illisible, ignoré")
        records = self.inner.daily(latitude, longitude, start, end)
        try:
            self._dir.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps([r.model_dump(mode="json") for r in records]), encoding="utf-8")
        except OSError:
            log.warning("cache non inscriptible, ignoré")
        return records

    def geocode(self, q, limit, language):
        return self.inner.geocode(q, limit, language)
