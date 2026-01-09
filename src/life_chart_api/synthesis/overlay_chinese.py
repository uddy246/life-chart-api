from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from zoneinfo import ZoneInfo
from typing import Any

_STEMS = ["jia", "yi", "bing", "ding", "wu", "ji", "geng", "xin", "ren", "gui"]
_BRANCHES = ["zi", "chou", "yin", "mao", "chen", "si", "wu", "wei", "shen", "you", "xu", "hai"]
_MONTH_BRANCHES = ["yin", "mao", "chen", "si", "wu", "wei", "shen", "you", "xu", "hai", "zi", "chou"]

_STEM_META = {
    "jia": ("wood", "yang"),
    "yi": ("wood", "yin"),
    "bing": ("fire", "yang"),
    "ding": ("fire", "yin"),
    "wu": ("earth", "yang"),
    "ji": ("earth", "yin"),
    "geng": ("metal", "yang"),
    "xin": ("metal", "yin"),
    "ren": ("water", "yang"),
    "gui": ("water", "yin"),
}

_BRANCH_ANIMALS = {
    "zi": "rat",
    "chou": "ox",
    "yin": "tiger",
    "mao": "rabbit",
    "chen": "dragon",
    "si": "snake",
    "wu": "horse",
    "wei": "goat",
    "shen": "monkey",
    "you": "rooster",
    "xu": "dog",
    "hai": "pig",
}

_FIRST_MONTH_STEM_BY_YEAR_STEM = {
    "jia": "bing",
    "ji": "bing",
    "yi": "wu",
    "geng": "wu",
    "bing": "geng",
    "xin": "geng",
    "ding": "ren",
    "ren": "ren",
    "wu": "jia",
    "gui": "jia",
}


@dataclass(frozen=True)
class ChineseTier1:
    pillars: dict[str, dict[str, str]]
    day_master: dict[str, str]
    elements: dict[str, Any]


def _normalize_time(time_str: str) -> str:
    parts = time_str.split(":")
    if len(parts) == 2:
        return f"{time_str}:00"
    if len(parts) == 3:
        return time_str
    raise ValueError("time must be HH:MM or HH:MM:SS")


def _local_datetime(date_str: str, time_str: str, tz_name: str) -> datetime:
    normalized_time = _normalize_time(time_str)
    tzinfo = ZoneInfo(tz_name)
    return datetime.strptime(
        f"{date_str} {normalized_time}", "%Y-%m-%d %H:%M:%S"
    ).replace(tzinfo=tzinfo)


def _sexagenary_index(base: date, target: date) -> int:
    delta = (target - base).days
    return delta % 60


def _year_pillar(year: int) -> tuple[str, str]:
    index = (year - 1984) % 60
    return _STEMS[index % 10], _BRANCHES[index % 12]


def _month_pillar(year_stem: str, month: int) -> tuple[str, str]:
    branch = _MONTH_BRANCHES[month - 1]
    first_stem = _FIRST_MONTH_STEM_BY_YEAR_STEM[year_stem]
    first_index = _STEMS.index(first_stem)
    stem = _STEMS[(first_index + (month - 1)) % 10]
    return stem, branch


def _day_pillar(local_dt: datetime) -> tuple[str, str]:
    base = date(1984, 2, 2)
    index = _sexagenary_index(base, local_dt.date())
    return _STEMS[index % 10], _BRANCHES[index % 12]


def _hour_branch(hour: int) -> str:
    index = ((hour + 1) // 2) % 12
    return _BRANCHES[index]


def _hour_pillar(day_stem: str, hour: int) -> tuple[str, str]:
    branch = _hour_branch(hour)
    stem_index = (_STEMS.index(day_stem) * 2 + _BRANCHES.index(branch)) % 10
    return _STEMS[stem_index], branch


def _element_distribution(stems: list[str]) -> dict[str, float]:
    counts = {element: 0 for element in ["wood", "fire", "earth", "metal", "water"]}
    for stem in stems:
        element = _STEM_META.get(stem, (None, None))[0]
        if element:
            counts[element] += 1
    total = max(1, sum(counts.values()))
    return {key: round(value / total * 100, 2) for key, value in counts.items()}


def compute_chinese_tier1(date_str: str, time_str: str, tz: str) -> ChineseTier1:
    local_dt = _local_datetime(date_str, time_str, tz)
    year_stem, year_branch = _year_pillar(local_dt.year)
    month_stem, month_branch = _month_pillar(year_stem, local_dt.month)
    day_stem, day_branch = _day_pillar(local_dt)
    hour_stem, hour_branch = _hour_pillar(day_stem, local_dt.hour)

    stems = [year_stem, month_stem, day_stem, hour_stem]
    distribution = _element_distribution(stems)
    favourable = sorted(distribution.items(), key=lambda item: (item[1], item[0]))
    favourable_elements = [favourable[0][0]]
    if len(favourable) > 1:
        favourable_elements.append(favourable[1][0])

    pillars = {
        "year": {"stem": year_stem, "branch": year_branch},
        "month": {"stem": month_stem, "branch": month_branch},
        "day": {"stem": day_stem, "branch": day_branch},
        "hour": {"stem": hour_stem, "branch": hour_branch},
    }
    day_master = {
        "stem": day_stem,
        "element": _STEM_META[day_stem][0],
        "yinYang": _STEM_META[day_stem][1],
    }
    elements = {"distribution": distribution, "favourable": favourable_elements}
    return ChineseTier1(pillars=pillars, day_master=day_master, elements=elements)


def _apply_pillar(target: dict[str, Any], pillar_data: dict[str, str]) -> None:
    if not isinstance(target, dict):
        return
    stem = pillar_data.get("stem")
    branch = pillar_data.get("branch")
    if stem in _STEM_META:
        target["stem"] = stem
        target["stemElement"] = _STEM_META[stem][0]
        target["stemYinYang"] = _STEM_META[stem][1]
    if branch in _BRANCH_ANIMALS:
        target["branch"] = branch
        target["branchAnimal"] = _BRANCH_ANIMALS[branch]


def overlay_chinese_tier1(
    chinese_template: dict[str, Any], computed: ChineseTier1
) -> dict[str, Any]:
    pillars = chinese_template.get("pillars")
    if isinstance(pillars, dict):
        for key in ("year", "month", "day", "hour"):
            if key in pillars and key in computed.pillars:
                _apply_pillar(pillars[key], computed.pillars[key])

    day_master = chinese_template.get("dayMaster")
    if isinstance(day_master, dict):
        day_master["stem"] = computed.day_master["stem"]
        day_master["element"] = computed.day_master["element"]
        day_master["yinYang"] = computed.day_master["yinYang"]

    elements = chinese_template.get("elements")
    if isinstance(elements, dict):
        distribution = elements.get("distribution")
        if isinstance(distribution, dict):
            for key, value in computed.elements["distribution"].items():
                distribution[key] = value
        elements["favourable"] = computed.elements["favourable"]

    return chinese_template
