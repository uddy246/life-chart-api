from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from life_chart_api.numerology.adapter import build_numerology_response_v1
from life_chart_api.numerology.schemas import NumerologyResponseV1
from life_chart_api.routes.profile_compute import router as profile_compute_router
from life_chart_api.routes.profile_stub import router as profile_router

app = FastAPI(title="Life Chart API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(profile_router)
app.include_router(profile_compute_router)


class NumerologyRequest(BaseModel):
    full_name_birth: str
    dob: str
    forecast_year: int | None = None
    as_of_date: str | None = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/numerology/compute", response_model=NumerologyResponseV1)
def compute_numerology(payload: NumerologyRequest) -> NumerologyResponseV1:
    return build_numerology_response_v1(
        full_name_birth=payload.full_name_birth,
        dob=payload.dob,
        forecast_year=payload.forecast_year,
        as_of_date=payload.as_of_date,
    )
