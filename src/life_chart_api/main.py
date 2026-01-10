from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel

from life_chart_api.errors import APIError, error_envelope
from life_chart_api.logging_config import configure_logging
from life_chart_api.middleware.rate_limit import create_rate_limit_middleware
from life_chart_api.middleware.metrics import metrics_middleware
from life_chart_api.middleware.request_id import request_id_middleware
from life_chart_api.middleware.request_logging import request_logging_middleware
from life_chart_api.middleware.version_headers import version_headers_middleware
from life_chart_api.metrics import METRICS
from life_chart_api.numerology.adapter import build_numerology_response_v1
from life_chart_api.numerology.schemas import NumerologyResponseV1
from life_chart_api.routes.profile_compute import router as profile_compute_router
from life_chart_api.routes.profile_forecast import router as profile_forecast_router
from life_chart_api.routes.profile_intersection import router as profile_intersection_router
from life_chart_api.routes.profile_narrative import router as profile_narrative_router
from life_chart_api.routes.profile_stub import router as profile_router
from life_chart_api.routes.profile_timeline import router as profile_timeline_router
from life_chart_api.settings import get_settings
from life_chart_api.versioning import (
    API_VERSION,
    SCHEMA_VERSION_ERROR,
    SCHEMA_VERSION_FORECAST,
    SCHEMA_VERSION_NARRATIVE,
    SCHEMA_VERSION_PROFILE,
    SCHEMA_VERSION_TIMELINE,
)

app = FastAPI(title="Life Chart API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://essence-unifier.lovable.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(profile_router)
app.include_router(profile_compute_router)
app.include_router(profile_timeline_router)
app.include_router(profile_forecast_router)
app.include_router(profile_narrative_router)
app.include_router(profile_intersection_router)
settings = get_settings()
configure_logging(settings.LOG_LEVEL)
app.middleware("http")(create_rate_limit_middleware(max_requests=settings.RATE_LIMIT_PER_MIN))
app.middleware("http")(metrics_middleware)
app.middleware("http")(request_logging_middleware)
app.middleware("http")(version_headers_middleware)
app.middleware("http")(request_id_middleware)


class NumerologyRequest(BaseModel):
    full_name_birth: str
    dob: str
    forecast_year: int | None = None
    as_of_date: str | None = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/meta")
def meta():
    return {
        "apiVersion": API_VERSION,
        "schemas": {
            "profile": SCHEMA_VERSION_PROFILE,
            "timeline": SCHEMA_VERSION_TIMELINE,
            "forecast": SCHEMA_VERSION_FORECAST,
            "narrative": SCHEMA_VERSION_NARRATIVE,
            "error": SCHEMA_VERSION_ERROR,
        },
    }


@app.get("/metrics")
def metrics():
    return METRICS.snapshot()


@app.get("/ready")
def ready():
    return {
        "status": "ready",
        "version": API_VERSION,
        "checks": {
            "schemasLoaded": True,
            "rateLimiter": "ok",
        },
    }


@app.post("/numerology/compute", response_model=NumerologyResponseV1)
def compute_numerology(payload: NumerologyRequest) -> NumerologyResponseV1:
    return build_numerology_response_v1(
        full_name_birth=payload.full_name_birth,
        dob=payload.dob,
        forecast_year=payload.forecast_year,
        as_of_date=payload.as_of_date,
    )


@app.exception_handler(APIError)
def handle_api_error(request, exc: APIError):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_envelope(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            request_id=getattr(request.state, "request_id", None),
        ),
    )


@app.exception_handler(RequestValidationError)
def handle_request_validation(request, exc: RequestValidationError):
    details = []
    for err in exc.errors():
        loc = ".".join(str(part) for part in err.get("loc", []))
        details.append({"path": loc or "request", "issue": err.get("msg", "invalid input")})
    return JSONResponse(
        status_code=422,
        content=error_envelope(
            code="INVALID_INPUT",
            message="Invalid request input.",
            details=details,
            request_id=getattr(request.state, "request_id", None),
        ),
    )


@app.exception_handler(HTTPException)
def handle_http_exception(request, exc: HTTPException):
    code = "NOT_FOUND" if exc.status_code == 404 else "INVALID_INPUT"
    message = exc.detail if isinstance(exc.detail, str) else "Request error."
    return JSONResponse(
        status_code=exc.status_code,
        content=error_envelope(
            code=code,
            message=message,
            request_id=getattr(request.state, "request_id", None),
        ),
    )


@app.exception_handler(Exception)
def handle_unhandled(request, __):
    return JSONResponse(
        status_code=500,
        content=error_envelope(
            code="INTERNAL_ERROR",
            message="Internal server error.",
            request_id=getattr(request.state, "request_id", None),
        ),
    )
