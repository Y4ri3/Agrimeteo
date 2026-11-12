"""Point d'entrée FastAPI : application, erreurs communes, CORS, /health."""

from __future__ import annotations

import logging
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import __version__
from app.api.v1.routes import router
from app.core import config
from app.core.errors import AppError
from app.schemas.common import Health

logging.basicConfig(level=config.LOG_LEVEL, format="%(asctime)s %(levelname)s %(name)s %(message)s")
# httpx journalise les URL (coordonnées exactes) : on ne garde que les valeurs arrondies (cahier 9.9).
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("agrimeteo")

app = FastAPI(
    title="AgriMétéo API",
    version=__version__,
    description="Contrat d'API d'AgriMétéo (v1).",
)

if config.CORS_ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ALLOWED_ORIGINS,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request.state.request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-Id"] = request.state.request_id
    return response


def _error(request: Request, status: int, code: str, message: str, details=None) -> JSONResponse:
    rid = getattr(request.state, "request_id", str(uuid.uuid4()))
    return JSONResponse(
        status_code=status,
        content={"error": {"code": code, "message": message, "details": details}, "request_id": rid},
    )


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return _error(request, exc.status, exc.code, exc.message, exc.details)


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    details = [
        {"field": ".".join(str(p) for p in e["loc"] if p not in ("query", "body")), "issue": e["msg"]}
        for e in exc.errors()
    ]
    return _error(request, 422, "VALIDATION_ERROR", "Vérifiez les coordonnées et les dates saisies.", details)


@app.exception_handler(Exception)
async def unexpected_handler(request: Request, exc: Exception):
    log.exception("erreur interne")  # la trace va dans les journaux, jamais dans la réponse
    return _error(request, 500, "INTERNAL_ERROR", "Une erreur est survenue.")


@app.get("/health", response_model=Health, tags=["health"])
def health():
    return Health(status="ok", version=__version__)


app.include_router(router)
