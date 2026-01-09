from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
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

_BRANCH_ELEMENTS = {
    "zi": "water",
    "chou": "earth",
    "yin": "wood",
    "mao": "wood",
    "chen": "earth",
    "si": "fire",
    "wu": "fire",
    "wei": "earth",
    "shen": "metal",
    "you": "metal",
    "xu": "earth",
    "hai": "water",
}

_ELEMENTS = ["wood", "fire", "earth", "metal", "water"]
_GENERATES = {
    "wood": "fire",
    "fire": "earth",
    "earth": "metal",
    "metal": "water",
    "water": "wood",
}
_CONTROLS = {
    "wood": "earth",
    "earth": "water",
    "water": "fire",
    "fire": "metal",
    "metal": "wood",
}

_TEN_GOD_DOMAINS = {
    "friend": ["self", "support"],
    "robWealth": ["competition", "drive"],
    "eatingGod": ["creativity", "expression"],
    "hurtingOfficer": ["independence", "challenge"],
    "directWealth": ["stability", "resources"],
    "indirectWealth": ["opportunity", "flexibility"],
    "directOfficer": ["discipline", "structure"],
    "sevenKillings": ["risk", "pressure"],
    "directResource": ["learning", "support"],
    "indirectResource": ["intuition", "adaptation"],
}


@dataclass(frozen=True)
class ChineseTier1:
    pillars: dict[str, dict[str, str]]
    day_master: dict[str, str]
    elements: dict[str, Any]

@dataclass(frozen=True)
class ChineseTier2:
    ten_gods_profile: list[dict[str, Any]]
    ten_gods_dominant: list[str]
    ten_gods_notes: str
    day_master_strength: str
    day_master_notes: str
    elements_distribution: dict[str, float]
    favourable_elements: list[str]
    unfavourable_elements: list[str]
    balance_advice: str
    luck_pillars: list[dict[str, Any]]
    luck_current: dict[str, Any]


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


def _element_relation(dm_element: str, other_element: str) -> str:
    if dm_element == other_element:
        return "same"
    if _GENERATES.get(other_element) == dm_element:
        return "resource"
    if _GENERATES.get(dm_element) == other_element:
        return "output"
    if _CONTROLS.get(dm_element) == other_element:
        return "wealth"
    return "authority"


def _ten_god(dm_element: str, dm_yin_yang: str, stem: str) -> str:
    other_element, other_yin_yang = _STEM_META[stem]
    relation = _element_relation(dm_element, other_element)
    same_polarity = dm_yin_yang == other_yin_yang

    if relation == "same":
        return "friend" if same_polarity else "robWealth"
    if relation == "resource":
        return "directResource" if same_polarity else "indirectResource"
    if relation == "output":
        return "eatingGod" if same_polarity else "hurtingOfficer"
    if relation == "wealth":
        return "directWealth" if same_polarity else "indirectWealth"
    return "directOfficer" if same_polarity else "sevenKillings"


def _score_strength(
    dm_element: str,
    month_branch: str,
    stems: list[str],
    branch_elements: list[str],
) -> tuple[int, list[str]]:
    score = 50
    evidence: list[str] = []

    month_element = _BRANCH_ELEMENTS.get(month_branch)
    if month_element:
        relation = _element_relation(dm_element, month_element)
        if relation == "same":
            score += 20
            evidence.append("month branch same element +20")
        elif relation == "resource":
            score += 15
            evidence.append("month branch resource +15")
        elif relation == "output":
            score -= 10
            evidence.append("month branch output -10")
        elif relation == "wealth":
            score -= 5
            evidence.append("month branch wealth -5")
        else:
            score -= 15
            evidence.append("month branch authority -15")

    for stem in stems:
        element = _STEM_META[stem][0]
        relation = _element_relation(dm_element, element)
        if relation == "same":
            score += 6
        elif relation == "resource":
            score += 4
        elif relation == "output":
            score -= 4
        elif relation == "wealth":
            score -= 3
        else:
            score -= 5
        evidence.append(f"stem {stem} {relation}")

    for element in branch_elements:
        relation = _element_relation(dm_element, element)
        if relation == "same":
            score += 3
        elif relation == "resource":
            score += 2
        elif relation == "output":
            score -= 2
        elif relation == "wealth":
            score -= 2
        else:
            score -= 3
        evidence.append(f"branch {element} {relation}")

    score = max(0, min(100, score))
    return score, evidence


def _strength_band(score: int) -> str:
    if score < 45:
        return "weak"
    if score < 65:
        return "balanced"
    return "strong"


def _favourable_elements(dm_element: str, strength: str) -> tuple[list[str], list[str]]:
    resource = None
    for element, generated in _GENERATES.items():
        if generated == dm_element:
            resource = element
            break
    output = _GENERATES.get(dm_element)
    wealth = _CONTROLS.get(dm_element)
    authority = None
    for element, controlled in _CONTROLS.items():
        if controlled == dm_element:
            authority = element
            break

    if strength == "weak":
        favourable = [dm_element, resource]
        unfavourable = [output, wealth, authority]
    elif strength == "strong":
        favourable = [output, wealth, authority]
        unfavourable = [dm_element, resource]
    else:
        favourable = [output, wealth]
        unfavourable = [resource]

    fav = [e for e in favourable if e in _ELEMENTS]
    unfav = [e for e in unfavourable if e in _ELEMENTS]
    return fav, unfav


def _luck_pillars(month_stem: str, month_branch: str, count: int = 8) -> list[dict[str, Any]]:
    pillars = []
    stem_index = _STEMS.index(month_stem)
    branch_index = _BRANCHES.index(month_branch)
    start_age = 7
    for idx in range(count):
        stem = _STEMS[(stem_index + idx) % 10]
        branch = _BRANCHES[(branch_index + idx) % 12]
        stem_element, stem_yin = _STEM_META[stem]
        pillars.append(
            {
                "index": idx,
                "startAge": start_age + idx * 10,
                "endAge": start_age + (idx + 1) * 10,
                "pillar": {
                    "stem": stem,
                    "branch": branch,
                    "stemElement": stem_element,
                    "stemYinYang": stem_yin,
                    "branchAnimal": _BRANCH_ANIMALS[branch],
                    "hiddenStems": [],
                    "notes": "",
                },
                "themes": [f"Luck pillar {idx + 1}"],
                "notes": "",
            }
        )
    return pillars


def compute_chinese_tier2(
    date_str: str, time_str: str, tz: str, tier1: ChineseTier1 | None = None
) -> ChineseTier2:
    if tier1 is None:
        tier1 = compute_chinese_tier1(date_str, time_str, tz)

    dm_stem = tier1.day_master["stem"]
    dm_element, dm_yin = _STEM_META[dm_stem]
    stems = [tier1.pillars["year"]["stem"], tier1.pillars["month"]["stem"], tier1.pillars["hour"]["stem"]]
    branch_elements = [
        _BRANCH_ELEMENTS[tier1.pillars["year"]["branch"]],
        _BRANCH_ELEMENTS[tier1.pillars["month"]["branch"]],
        _BRANCH_ELEMENTS[tier1.pillars["day"]["branch"]],
        _BRANCH_ELEMENTS[tier1.pillars["hour"]["branch"]],
    ]

    ten_gods = []
    weights = {"year": 0.35, "month": 0.4, "hour": 0.25}
    for key in ("year", "month", "hour"):
        stem = tier1.pillars[key]["stem"]
        ten_key = _ten_god(dm_element, dm_yin, stem)
        ten_gods.append(
            {
                "key": ten_key,
                "weight": weights[key],
                "domains": _TEN_GOD_DOMAINS[ten_key],
                "notes": f"{key} stem {stem}",
            }
        )

    ten_gods_sorted = sorted(ten_gods, key=lambda item: (-item["weight"], item["key"]))
    dominant = []
    for item in ten_gods_sorted:
        if item["key"] not in dominant:
            dominant.append(item["key"])
        if len(dominant) == 2:
            break

    score, evidence = _score_strength(
        dm_element, tier1.pillars["month"]["branch"], stems, branch_elements
    )
    strength = _strength_band(score)
    fav, unfav = _favourable_elements(dm_element, strength)

    distribution = _element_distribution(
        [
            tier1.pillars["year"]["stem"],
            tier1.pillars["month"]["stem"],
            tier1.pillars["day"]["stem"],
            tier1.pillars["hour"]["stem"],
        ]
    )
    luck_pillars = _luck_pillars(
        tier1.pillars["month"]["stem"], tier1.pillars["month"]["branch"]
    )
    today = datetime.now(timezone.utc).date()
    birth = date.fromisoformat(date_str)
    age = max(0, today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day)))
    current_index = max(0, min(len(luck_pillars) - 1, (age - 7) // 10))
    current = {
        "pillarIndex": current_index,
        "theme": f"Luck pillar {current_index + 1}",
        "advice": f"Focus on {', '.join(fav) if fav else 'balance'}.",
    }

    ten_notes = ", ".join([f"{item['key']}({item['weight']})" for item in ten_gods_sorted])
    day_notes = f"Score {score}; " + "; ".join(evidence[:6])
    balance_advice = (
        f"Day master {strength}. Favour {', '.join(fav)}; reduce {', '.join(unfav)}."
    )

    return ChineseTier2(
        ten_gods_profile=ten_gods_sorted,
        ten_gods_dominant=dominant,
        ten_gods_notes=ten_notes,
        day_master_strength=strength,
        day_master_notes=day_notes,
        elements_distribution=distribution,
        favourable_elements=fav or [dm_element],
        unfavourable_elements=unfav,
        balance_advice=balance_advice,
        luck_pillars=luck_pillars,
        luck_current=current,
    )


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


def overlay_chinese_tier2(
    chinese_template: dict[str, Any], computed: ChineseTier2
) -> dict[str, Any]:
    ten_gods = chinese_template.get("tenGods")
    if isinstance(ten_gods, dict):
        ten_gods["profile"] = computed.ten_gods_profile
        ten_gods["dominant"] = computed.ten_gods_dominant
        ten_gods["notes"] = computed.ten_gods_notes

    day_master = chinese_template.get("dayMaster")
    if isinstance(day_master, dict):
        day_master["strength"] = computed.day_master_strength
        day_master["notes"] = computed.day_master_notes

    elements = chinese_template.get("elements")
    if isinstance(elements, dict):
        distribution = elements.get("distribution")
        if isinstance(distribution, dict):
            for key, value in computed.elements_distribution.items():
                distribution[key] = value
        elements["favourable"] = computed.favourable_elements
        elements["unfavourable"] = computed.unfavourable_elements
        elements["balanceAdvice"] = computed.balance_advice

    luck_cycles = chinese_template.get("luckCycles")
    if isinstance(luck_cycles, dict):
        luck_cycles["startAge"] = 7
        luck_cycles["direction"] = "forward"
        luck_cycles["pillars"] = computed.luck_pillars
        luck_cycles["current"] = computed.luck_current

    return chinese_template
