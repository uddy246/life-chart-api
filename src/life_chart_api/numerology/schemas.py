# src/life_chart_api/numerology/schemas.py
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional, Literal

from pydantic import BaseModel, Field, ConfigDict

from pydantic import BaseModel, ConfigDict

class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

class NumerologyPolicies(StrictBaseModel):
    vowels: str = "AEIOUY_ALWAYS"
    life_path_method: str = "YYYYMMDD_DIGIT_SUM"
    masters: List[int] = [11, 22, 33]
    karmic_debts: List[int] = [13, 14, 16, 19]
    keep_masters_personal_year: bool = False


# -------------------------
# Core sub-models
# -------------------------

class ReductionModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start_value: int
    steps: List[int]
    final_value: int
    is_master: bool
    base_value: Optional[int] = None


class PrimitiveFlagsModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_master: bool
    has_karmic_debt: bool


class PrimitiveModel(BaseModel):
    """
    Canonical math-only primitive output model (v1).
    """
    model_config = ConfigDict(extra="forbid")

    key: str
    raw: Dict[str, Any]
    reduction: ReductionModel
    flags: PrimitiveFlagsModel


# -------------------------
# Engine response envelope
# -------------------------

class NumerologySystemMeta(StrictBaseModel):
    system: str = Field(default="numerology")
    variant: str = Field(default="pythagorean")
    version: str = Field(default="1.0")
    policies: NumerologyPolicies = Field(default_factory=NumerologyPolicies)



class NumerologyInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dob: str
    full_name_birth_raw: str
    full_name_birth_normalized: str

    # temporal context (optional)
    as_of_date: Optional[str] = None
    forecast_year: Optional[int] = None


class NumerologyResponseV1(BaseModel):
    """
    v1 response: includes meta, inputs, primitives.
    We will add signals/claims/synthesis in later iterations.
    """
    model_config = ConfigDict(extra="forbid")

    system_meta: NumerologySystemMeta
    inputs: NumerologyInputs
    primitives: Dict[str, PrimitiveModel]
