# src/life_chart_api/numerology/compute.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

from life_chart_api.numerology.utils import (
    KARMIC_DEBT_SET,
    ReductionResult,
    normalize_name,
    reduce_number,
    sum_consonants,
    sum_name,
    sum_vowels,
)


# -------------------------
# Data structures (math-only)
# -------------------------

@dataclass(frozen=True)
class PrimitiveResult:
    """
    Math-only output for a numerology primitive.

    - raw_* fields capture trace components
    - reduction stores the reduction steps + master/base handling
    - flags are computed deterministically (no prose)
    """
    key: str
    raw: Dict[str, Any]
    reduction: ReductionResult
    flags: Dict[str, Any]


# -------------------------
# DOB helpers
# -------------------------

def _parse_dob(dob: str | date) -> date:
    if isinstance(dob, date):
        return dob
    if not isinstance(dob, str):
        raise TypeError(f"dob must be str or date, got {type(dob).__name__}")
    try:
        return datetime.strptime(dob, "%Y-%m-%d").date()
    except ValueError as e:
        raise ValueError("dob must be ISO format YYYY-MM-DD") from e


def _digits_yyyymmdd(d: date) -> List[int]:
    s = f"{d.year:04d}{d.month:02d}{d.day:02d}"
    return [int(ch) for ch in s]


def _digit_sum_year(year: int) -> int:
    return sum(int(ch) for ch in str(year))


def _karmic_flag_from_steps(steps: List[int]) -> bool:
    """
    v1 policy (per spec): karmic debt is flagged if raw sum OR any intermediate step
    hits a karmic debt number.
    """
    return any(step in KARMIC_DEBT_SET for step in steps)


# -------------------------
# Primitive computations
# -------------------------

def compute_life_path(dob: str | date) -> PrimitiveResult:
    """
    Spec: digit_sum_full_date_YYYYMMDD
      - sum digits of YYYYMMDD
      - reduce with masters preserved
    """
    d = _parse_dob(dob)
    digits = _digits_yyyymmdd(d)
    raw_sum = sum(digits)

    reduction = reduce_number(raw_sum, keep_masters=True)
    karmic = _karmic_flag_from_steps(reduction.steps)

    return PrimitiveResult(
        key="life_path",
        raw={"dob": d.isoformat(), "digits_yyyymmdd": digits, "digit_sum": raw_sum},
        reduction=reduction,
        flags={"is_master": reduction.is_master, "has_karmic_debt": karmic},
    )


def compute_expression(full_name_birth: str) -> PrimitiveResult:
    """
    Spec: sum of full normalised birth name, reduced with masters preserved.
    """
    name_norm = normalize_name(full_name_birth)
    raw_sum = sum_name(name_norm)

    reduction = reduce_number(raw_sum, keep_masters=True)
    karmic = _karmic_flag_from_steps(reduction.steps)

    return PrimitiveResult(
        key="expression",
        raw={"full_name_birth_raw": full_name_birth, "full_name_birth_normalized": name_norm, "name_sum": raw_sum},
        reduction=reduction,
        flags={"is_master": reduction.is_master, "has_karmic_debt": karmic},
    )


def compute_soul_urge(full_name_birth: str) -> PrimitiveResult:
    """
    Spec: vowels-only sum, reduced with masters preserved. Vowels policy AEIOUY.
    """
    name_norm = normalize_name(full_name_birth)
    raw_sum = sum_vowels(name_norm)

    reduction = reduce_number(raw_sum, keep_masters=True)
    karmic = _karmic_flag_from_steps(reduction.steps)

    return PrimitiveResult(
        key="soul_urge",
        raw={"full_name_birth_raw": full_name_birth, "full_name_birth_normalized": name_norm, "vowel_sum": raw_sum},
        reduction=reduction,
        flags={"is_master": reduction.is_master, "has_karmic_debt": karmic},
    )


def compute_personality(full_name_birth: str) -> PrimitiveResult:
    """
    Spec: consonants-only sum, reduced with masters preserved. Consonants = not in AEIOUY.
    """
    name_norm = normalize_name(full_name_birth)
    raw_sum = sum_consonants(name_norm)

    reduction = reduce_number(raw_sum, keep_masters=True)
    karmic = _karmic_flag_from_steps(reduction.steps)

    return PrimitiveResult(
        key="personality",
        raw={"full_name_birth_raw": full_name_birth, "full_name_birth_normalized": name_norm, "consonant_sum": raw_sum},
        reduction=reduction,
        flags={"is_master": reduction.is_master, "has_karmic_debt": karmic},
    )


def compute_birthday(dob: str | date) -> PrimitiveResult:
    """
    Spec: reduce day-of-month with masters preserved.
    """
    d = _parse_dob(dob)
    day = d.day

    reduction = reduce_number(day, keep_masters=True)
    karmic = _karmic_flag_from_steps(reduction.steps)

    return PrimitiveResult(
        key="birthday",
        raw={"dob": d.isoformat(), "day": day},
        reduction=reduction,
        flags={"is_master": reduction.is_master, "has_karmic_debt": karmic},
    )


def compute_attitude(dob: str | date) -> PrimitiveResult:
    """
    Spec: reduce(month + day) with masters preserved.
    """
    d = _parse_dob(dob)
    raw_sum = d.month + d.day

    reduction = reduce_number(raw_sum, keep_masters=True)
    karmic = _karmic_flag_from_steps(reduction.steps)

    return PrimitiveResult(
        key="attitude",
        raw={"dob": d.isoformat(), "month": d.month, "day": d.day, "month_plus_day": raw_sum},
        reduction=reduction,
        flags={"is_master": reduction.is_master, "has_karmic_debt": karmic},
    )


def compute_maturity(life_path: PrimitiveResult, expression: PrimitiveResult) -> PrimitiveResult:
    """
    Spec: reduce(life_path.value + expression.value) with masters preserved.
    Use displayed values (final_value), not raw sums.
    """
    lp_val = life_path.reduction.final_value
    ex_val = expression.reduction.final_value
    raw_sum = lp_val + ex_val

    reduction = reduce_number(raw_sum, keep_masters=True)
    karmic = _karmic_flag_from_steps(reduction.steps)

    return PrimitiveResult(
        key="maturity",
        raw={"life_path_value": lp_val, "expression_value": ex_val, "sum": raw_sum},
        reduction=reduction,
        flags={"is_master": reduction.is_master, "has_karmic_debt": karmic},
    )


def compute_personal_year(
    dob: str | date,
    forecast_year: Optional[int] = None,
    as_of_date: Optional[str | date] = None,
) -> PrimitiveResult:
    """
    Spec: reduce(birth_month + birth_day + digit_sum(target_year))

    v1 policy: keep_masters_personal_year = False
    """
    d = _parse_dob(dob)

    if forecast_year is None:
        if as_of_date is None:
            target_year = date.today().year
        else:
            target_year = _parse_dob(as_of_date).year
    else:
        target_year = int(forecast_year)

    year_sum = _digit_sum_year(target_year)
    raw_sum = d.month + d.day + year_sum

    reduction = reduce_number(raw_sum, keep_masters=False)
    karmic = _karmic_flag_from_steps(reduction.steps)

    return PrimitiveResult(
        key="personal_year",
        raw={
            "dob": d.isoformat(),
            "birth_month": d.month,
            "birth_day": d.day,
            "target_year": target_year,
            "target_year_digit_sum": year_sum,
            "sum": raw_sum,
            "keep_masters": False,
        },
        reduction=reduction,
        flags={"is_master": reduction.is_master, "has_karmic_debt": karmic},
    )


# -------------------------
# Convenience: compute all v1 primitives
# -------------------------

def compute_primitives_v1(
    full_name_birth: str,
    dob: str | date,
    forecast_year: Optional[int] = None,
    as_of_date: Optional[str | date] = None,
) -> Dict[str, PrimitiveResult]:
    """
    Returns a dict of PrimitiveResult keyed by primitive key.

    v1 includes:
      life_path, expression, soul_urge, personality, birthday, attitude, maturity, personal_year
    """
    life_path = compute_life_path(dob)
    expression = compute_expression(full_name_birth)
    soul_urge = compute_soul_urge(full_name_birth)
    personality = compute_personality(full_name_birth)
    birthday = compute_birthday(dob)
    attitude = compute_attitude(dob)
    maturity = compute_maturity(life_path, expression)
    personal_year = compute_personal_year(dob, forecast_year=forecast_year, as_of_date=as_of_date)

    return {
        "life_path": life_path,
        "expression": expression,
        "soul_urge": soul_urge,
        "personality": personality,
        "birthday": birthday,
        "attitude": attitude,
        "maturity": maturity,
        "personal_year": personal_year,
    }
# -------------------------
# Convenience: compute all v1 primitives
# -------------------------

def compute_primitives_v1(
    full_name_birth: str,
    dob: str | date,
    forecast_year: Optional[int] = None,
    as_of_date: Optional[str | date] = None,
) -> Dict[str, PrimitiveResult]:
    """
    Returns a dict of PrimitiveResult keyed by primitive key.

    v1 includes:
      life_path, expression, soul_urge, personality,
      birthday, attitude, maturity, personal_year
    """
    life_path = compute_life_path(dob)
    expression = compute_expression(full_name_birth)
    soul_urge = compute_soul_urge(full_name_birth)
    personality = compute_personality(full_name_birth)
    birthday = compute_birthday(dob)
    attitude = compute_attitude(dob)
    maturity = compute_maturity(life_path, expression)
    personal_year = compute_personal_year(
        dob,
        forecast_year=forecast_year,
        as_of_date=as_of_date,
    )

    return {
        "life_path": life_path,
        "expression": expression,
        "soul_urge": soul_urge,
        "personality": personality,
        "birthday": birthday,
        "attitude": attitude,
        "maturity": maturity,
        "personal_year": personal_year,
    }
