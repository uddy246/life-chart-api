# src/life_chart_api/numerology/adapter.py
from __future__ import annotations

from typing import Any, Dict, Optional

from life_chart_api.numerology.compute import PrimitiveResult, compute_primitives_v1
from life_chart_api.numerology.utils import normalize_name
from life_chart_api.numerology.schemas import (
    NumerologyInputs,
    NumerologyResponseV1,
    NumerologySystemMeta,
    PrimitiveFlagsModel,
    PrimitiveModel,
    ReductionModel,
)


def _to_reduction_model(r) -> ReductionModel:
    # r is ReductionResult (dataclass) from utils.py
    return ReductionModel(
        start_value=r.start_value,
        steps=list(r.steps),
        final_value=r.final_value,
        is_master=r.is_master,
        base_value=r.base_value,
    )


def _to_primitive_model(p: PrimitiveResult) -> PrimitiveModel:
    return PrimitiveModel(
        key=p.key,
        raw=dict(p.raw),
        reduction=_to_reduction_model(p.reduction),
        flags=PrimitiveFlagsModel(
            is_master=bool(p.flags.get("is_master", False)),
            has_karmic_debt=bool(p.flags.get("has_karmic_debt", False)),
        ),
    )


def build_numerology_response_v1(
    *,
    full_name_birth: str,
    dob: str,
    forecast_year: Optional[int] = None,
    as_of_date: Optional[str] = None,
) -> NumerologyResponseV1:
    """
    High-level builder:
      - computes primitives (math layer)
      - adapts to canonical Pydantic response schema (v1)
    """
    name_norm = normalize_name(full_name_birth)

    primitives_dc = compute_primitives_v1(
        full_name_birth=full_name_birth,
        dob=dob,
        forecast_year=forecast_year,
        as_of_date=as_of_date,
    )

    primitives: Dict[str, PrimitiveModel] = {
        k: _to_primitive_model(v) for k, v in primitives_dc.items()
    }

    return NumerologyResponseV1(
        system_meta=NumerologySystemMeta(),
        inputs=NumerologyInputs(
            dob=dob,
            full_name_birth_raw=full_name_birth,
            full_name_birth_normalized=name_norm,
            as_of_date=as_of_date,
            forecast_year=forecast_year,
        ),
        primitives=primitives,
    )
