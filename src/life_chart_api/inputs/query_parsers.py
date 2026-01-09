from __future__ import annotations

import re
from datetime import date
from typing import Iterable

from life_chart_api.errors import APIError

_YM_PATTERN = re.compile(r"^\d{4}-\d{2}$")
_YMD_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_ym(value: str, *, path: str) -> str:
    if not isinstance(value, str) or not _YM_PATTERN.match(value):
        raise APIError(
            code="INVALID_INPUT",
            message="Invalid year-month format.",
            details=[{"path": path, "issue": "must match YYYY-MM"}],
            status_code=400,
        )
    year, month = value.split("-")
    if not (1 <= int(month) <= 12):
        raise APIError(
            code="INVALID_INPUT",
            message="Invalid year-month value.",
            details=[{"path": path, "issue": "month must be 01-12"}],
            status_code=400,
        )
    return f"{int(year):04d}-{int(month):02d}"


def parse_ymd(value: str, *, path: str) -> str:
    if not isinstance(value, str) or not _YMD_PATTERN.match(value):
        raise APIError(
            code="INVALID_INPUT",
            message="Invalid date format.",
            details=[{"path": path, "issue": "must match YYYY-MM-DD"}],
            status_code=400,
        )
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise APIError(
            code="INVALID_INPUT",
            message="Invalid date value.",
            details=[{"path": path, "issue": str(exc)}],
            status_code=400,
        ) from exc
    return parsed.strftime("%Y-%m-%d")


def parse_include_csv(value: str | None, *, allowed: Iterable[str], default: str, path: str) -> list[str]:
    allowed_set = set(allowed)
    raw = value if value is not None else default
    items = [item.strip() for item in raw.split(",") if item.strip()]
    invalid = [item for item in items if item not in allowed_set]
    if invalid:
        raise APIError(
            code="INVALID_INPUT",
            message="Invalid include parameter.",
            details=[{"path": path, "issue": f"unsupported values: {', '.join(invalid)}"}],
            status_code=400,
        )
    return items


def parse_granularity(value: str | None, *, path: str) -> str:
    if value is None:
        return "month"
    if value not in {"month", "quarter"}:
        raise APIError(
            code="INVALID_INPUT",
            message="Invalid granularity.",
            details=[{"path": path, "issue": "must be month or quarter"}],
            status_code=400,
        )
    return value


def parse_tone(value: str | None, *, path: str) -> str:
    if value is None:
        return "neutral"
    if value not in {"neutral", "direct", "reflective"}:
        raise APIError(
            code="INVALID_INPUT",
            message="Invalid tone.",
            details=[{"path": path, "issue": "must be neutral, direct, or reflective"}],
            status_code=400,
        )
    return value


def validate_range(
    *,
    range_from: str,
    range_to: str,
    granularity: str,
    path_from: str,
    path_to: str,
    max_months: int = 60,
    max_quarters: int = 80,
) -> tuple[str, str]:
    start = parse_ym(range_from, path=path_from)
    end = parse_ym(range_to, path=path_to)
    start_year, start_month = map(int, start.split("-"))
    end_year, end_month = map(int, end.split("-"))
    start_index = start_year * 12 + (start_month - 1)
    end_index = end_year * 12 + (end_month - 1)
    if end_index < start_index:
        raise APIError(
            code="INVALID_INPUT",
            message="Invalid range.",
            details=[{"path": path_to, "issue": "must be greater than or equal to from"}],
            status_code=400,
        )
    months = end_index - start_index + 1
    if granularity == "quarter":
        if months > max_quarters * 3:
            raise APIError(
                code="INVALID_INPUT",
                message="Range too large for quarter granularity.",
                details=[{"path": "query.range", "issue": f"max {max_quarters} quarters"}],
                status_code=400,
            )
    else:
        if months > max_months:
            raise APIError(
                code="INVALID_INPUT",
                message="Range too large for month granularity.",
                details=[{"path": "query.range", "issue": f"max {max_months} months"}],
                status_code=400,
            )
    return start, end
