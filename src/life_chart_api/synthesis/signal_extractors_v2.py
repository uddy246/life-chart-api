from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

_ELEMENT_BY_SIGN = {
    "aries": "fire",
    "leo": "fire",
    "sagittarius": "fire",
    "taurus": "earth",
    "virgo": "earth",
    "capricorn": "earth",
    "gemini": "air",
    "libra": "air",
    "aquarius": "air",
    "cancer": "water",
    "scorpio": "water",
    "pisces": "water",
}

_SYSTEM_ORDER = ("western", "vedic", "chinese", "numerology")


@dataclass(frozen=True)
class EvidenceV2:
    system: str
    weight: float
    source: str
    value: object
    note: str


@dataclass(frozen=True)
class CanonicalSignal:
    id: str
    domain: str
    polarity: str
    strength: float
    evidence: list[EvidenceV2]


def _normalize_sign(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    return value.strip().lower()


def _element_for_sign(sign: str | None) -> str | None:
    if not sign:
        return None
    return _ELEMENT_BY_SIGN.get(sign)


def _planet_sign(western: dict[str, Any], planet_name: str) -> str | None:
    planets = western.get("planets")
    if not isinstance(planets, list):
        return None
    for planet in planets:
        if isinstance(planet, dict) and planet.get("planet") == planet_name:
            return _normalize_sign(planet.get("sign"))
    return None


def _signal(
    *,
    signal_id: str,
    domain: str,
    polarity: str,
    strength: float,
    system: str,
    source: str,
    value: object,
    note: str,
) -> CanonicalSignal:
    return CanonicalSignal(
        id=signal_id,
        domain=domain,
        polarity=polarity,
        strength=round(max(0.0, min(1.0, strength)), 2),
        evidence=[
            EvidenceV2(
                system=system,
                weight=round(max(0.0, min(1.0, strength)), 2),
                source=source,
                value=value,
                note=note,
            )
        ],
    )


def extract_western_signals_v2(western: dict[str, Any]) -> list[CanonicalSignal]:
    signals: list[CanonicalSignal] = []

    mercury = _planet_sign(western, "mercury")
    mars = _planet_sign(western, "mars")
    saturn = _planet_sign(western, "saturn")
    venus = _planet_sign(western, "venus")
    sun = _normalize_sign(western.get("identity", {}).get("sunSign", {}).get("sign"))
    moon = _normalize_sign(western.get("identity", {}).get("moonSign", {}).get("sign"))
    asc = _normalize_sign(western.get("identity", {}).get("ascendant", {}).get("sign"))

    merc_elem = _element_for_sign(mercury)
    if merc_elem in ("air", "earth"):
        signals.append(
            _signal(
                signal_id="analytical_mind",
                domain="mind",
                polarity="supporting",
                strength=0.6,
                system="western",
                source="western.planets.mercury.sign",
                value=mercury,
                note="Mercury in air/earth element.",
            )
        )
    elif merc_elem == "water":
        signals.append(
            _signal(
                signal_id="creativity_expression",
                domain="mind",
                polarity="supporting",
                strength=0.55,
                system="western",
                source="western.planets.mercury.sign",
                value=mercury,
                note="Mercury in water element.",
            )
        )
    elif merc_elem == "fire":
        signals.append(
            _signal(
                signal_id="ambition_drive",
                domain="energy",
                polarity="supporting",
                strength=0.5,
                system="western",
                source="western.planets.mercury.sign",
                value=mercury,
                note="Mercury in fire element.",
            )
        )

    mars_elem = _element_for_sign(mars)
    if mars_elem in ("fire", "earth"):
        signals.append(
            _signal(
                signal_id="ambition_drive",
                domain="energy",
                polarity="supporting",
                strength=0.6,
                system="western",
                source="western.planets.mars.sign",
                value=mars,
                note="Mars in fire/earth element.",
            )
        )
    elif mars_elem == "water":
        signals.append(
            _signal(
                signal_id="emotional_intensity",
                domain="personality",
                polarity="supporting",
                strength=0.5,
                system="western",
                source="western.planets.mars.sign",
                value=mars,
                note="Mars in water element.",
            )
        )
    elif mars_elem == "air":
        signals.append(
            _signal(
                signal_id="independence_autonomy",
                domain="growth",
                polarity="supporting",
                strength=0.5,
                system="western",
                source="western.planets.mars.sign",
                value=mars,
                note="Mars in air element.",
            )
        )

    saturn_elem = _element_for_sign(saturn)
    if saturn_elem:
        signals.append(
            _signal(
                signal_id="structure_discipline",
                domain="growth",
                polarity="supporting",
                strength=0.6,
                system="western",
                source="western.planets.saturn.sign",
                value=saturn,
                note="Saturn sign captured.",
            )
        )

    venus_elem = _element_for_sign(venus)
    if venus_elem in ("air", "water"):
        signals.append(
            _signal(
                signal_id="social_harmony",
                domain="relationships",
                polarity="supporting",
                strength=0.55,
                system="western",
                source="western.planets.venus.sign",
                value=venus,
                note="Venus in air/water element.",
            )
        )
    elif venus_elem == "earth":
        signals.append(
            _signal(
                signal_id="stability_security",
                domain="relationships",
                polarity="supporting",
                strength=0.5,
                system="western",
                source="western.planets.venus.sign",
                value=venus,
                note="Venus in earth element.",
            )
        )
    elif venus_elem == "fire":
        signals.append(
            _signal(
                signal_id="creativity_expression",
                domain="relationships",
                polarity="supporting",
                strength=0.45,
                system="western",
                source="western.planets.venus.sign",
                value=venus,
                note="Venus in fire element.",
            )
        )

    sun_elem = _element_for_sign(sun)
    if sun_elem == "fire":
        signals.append(
            _signal(
                signal_id="ambition_drive",
                domain="career",
                polarity="supporting",
                strength=0.4,
                system="western",
                source="western.identity.sunSign",
                value=sun,
                note="Sun in fire element.",
            )
        )
    elif sun_elem == "earth":
        signals.append(
            _signal(
                signal_id="grounded_pragmatism",
                domain="personality",
                polarity="supporting",
                strength=0.4,
                system="western",
                source="western.identity.sunSign",
                value=sun,
                note="Sun in earth element.",
            )
        )
    elif sun_elem == "water":
        signals.append(
            _signal(
                signal_id="emotional_intensity",
                domain="personality",
                polarity="supporting",
                strength=0.4,
                system="western",
                source="western.identity.sunSign",
                value=sun,
                note="Sun in water element.",
            )
        )
    elif sun_elem == "air":
        signals.append(
            _signal(
                signal_id="social_harmony",
                domain="relationships",
                polarity="supporting",
                strength=0.4,
                system="western",
                source="western.identity.sunSign",
                value=sun,
                note="Sun in air element.",
            )
        )

    moon_elem = _element_for_sign(moon)
    if moon_elem == "water":
        signals.append(
            _signal(
                signal_id="emotional_intensity",
                domain="personality",
                polarity="supporting",
                strength=0.45,
                system="western",
                source="western.identity.moonSign",
                value=moon,
                note="Moon in water element.",
            )
        )
    elif moon_elem == "earth":
        signals.append(
            _signal(
                signal_id="stability_security",
                domain="personality",
                polarity="supporting",
                strength=0.45,
                system="western",
                source="western.identity.moonSign",
                value=moon,
                note="Moon in earth element.",
            )
        )
    elif moon_elem == "air":
        signals.append(
            _signal(
                signal_id="analytical_mind",
                domain="mind",
                polarity="supporting",
                strength=0.4,
                system="western",
                source="western.identity.moonSign",
                value=moon,
                note="Moon in air element.",
            )
        )
    elif moon_elem == "fire":
        signals.append(
            _signal(
                signal_id="ambition_drive",
                domain="energy",
                polarity="supporting",
                strength=0.4,
                system="western",
                source="western.identity.moonSign",
                value=moon,
                note="Moon in fire element.",
            )
        )

    asc_elem = _element_for_sign(asc)
    if asc_elem == "fire":
        signals.append(
            _signal(
                signal_id="independence_autonomy",
                domain="growth",
                polarity="supporting",
                strength=0.4,
                system="western",
                source="western.identity.ascendant",
                value=asc,
                note="Ascendant in fire element.",
            )
        )
    elif asc_elem == "air":
        signals.append(
            _signal(
                signal_id="communication_social",
                domain="relationships",
                polarity="supporting",
                strength=0.4,
                system="western",
                source="western.identity.ascendant",
                value=asc,
                note="Ascendant in air element.",
            )
        )
    elif asc_elem == "earth":
        signals.append(
            _signal(
                signal_id="grounded_pragmatism",
                domain="personality",
                polarity="supporting",
                strength=0.4,
                system="western",
                source="western.identity.ascendant",
                value=asc,
                note="Ascendant in earth element.",
            )
        )
    elif asc_elem == "water":
        signals.append(
            _signal(
                signal_id="emotional_intensity",
                domain="personality",
                polarity="supporting",
                strength=0.4,
                system="western",
                source="western.identity.ascendant",
                value=asc,
                note="Ascendant in water element.",
            )
        )

    return signals


def extract_vedic_signals_v2(vedic: dict[str, Any]) -> list[CanonicalSignal]:
    signals: list[CanonicalSignal] = []
    lagna = _normalize_sign(vedic.get("lagna_sign"))
    moon = _normalize_sign(vedic.get("moon_sign"))
    saturn_theme = vedic.get("saturn_theme")
    rahu_ketu = vedic.get("rahu_ketu_emphasis")

    lagna_elem = _element_for_sign(lagna)
    if lagna_elem == "fire":
        signals.append(
            _signal(
                signal_id="ambition_drive",
                domain="personality",
                polarity="supporting",
                strength=0.5,
                system="vedic",
                source="vedic.lagna_sign",
                value=lagna,
                note="Lagna in fire element.",
            )
        )
    elif lagna_elem == "earth":
        signals.append(
            _signal(
                signal_id="grounded_pragmatism",
                domain="personality",
                polarity="supporting",
                strength=0.5,
                system="vedic",
                source="vedic.lagna_sign",
                value=lagna,
                note="Lagna in earth element.",
            )
        )
    elif lagna_elem == "air":
        signals.append(
            _signal(
                signal_id="analytical_mind",
                domain="mind",
                polarity="supporting",
                strength=0.5,
                system="vedic",
                source="vedic.lagna_sign",
                value=lagna,
                note="Lagna in air element.",
            )
        )
    elif lagna_elem == "water":
        signals.append(
            _signal(
                signal_id="emotional_intensity",
                domain="personality",
                polarity="supporting",
                strength=0.5,
                system="vedic",
                source="vedic.lagna_sign",
                value=lagna,
                note="Lagna in water element.",
            )
        )

    moon_elem = _element_for_sign(moon)
    if moon_elem == "water":
        signals.append(
            _signal(
                signal_id="emotional_intensity",
                domain="personality",
                polarity="supporting",
                strength=0.5,
                system="vedic",
                source="vedic.moon_sign",
                value=moon,
                note="Moon in water element.",
            )
        )
    elif moon_elem == "earth":
        signals.append(
            _signal(
                signal_id="stability_security",
                domain="personality",
                polarity="supporting",
                strength=0.5,
                system="vedic",
                source="vedic.moon_sign",
                value=moon,
                note="Moon in earth element.",
            )
        )

    if isinstance(saturn_theme, str) and saturn_theme:
        signals.append(
            _signal(
                signal_id="structure_discipline",
                domain="growth",
                polarity="supporting",
                strength=0.5,
                system="vedic",
                source="vedic.saturn_theme",
                value=saturn_theme,
                note="Saturn theme present.",
            )
        )

    if isinstance(rahu_ketu, bool) and rahu_ketu:
        signals.append(
            _signal(
                signal_id="unconventional_path",
                domain="growth",
                polarity="supporting",
                strength=0.55,
                system="vedic",
                source="vedic.rahu_ketu_emphasis",
                value=rahu_ketu,
                note="Rahu/Ketu emphasis.",
            )
        )
        signals.append(
            _signal(
                signal_id="spiritual_intensity",
                domain="growth",
                polarity="supporting",
                strength=0.45,
                system="vedic",
                source="vedic.rahu_ketu_emphasis",
                value=rahu_ketu,
                note="Rahu/Ketu emphasis.",
            )
        )

    return signals


def extract_chinese_signals_v2(chinese: dict[str, Any]) -> list[CanonicalSignal]:
    signals: list[CanonicalSignal] = []
    day_master = chinese.get("dayMaster", {})
    elements = chinese.get("elements", {})
    ten_gods = chinese.get("tenGods", {})

    dm_element = day_master.get("element") if isinstance(day_master, dict) else None
    dm_strength = day_master.get("strength") if isinstance(day_master, dict) else None

    if isinstance(dm_strength, str):
        polarity = "supporting" if dm_strength == "strong" else "challenging"
        signals.append(
            _signal(
                signal_id="resilience_endurance",
                domain="growth",
                polarity=polarity,
                strength=0.6,
                system="chinese",
                source="chinese.dayMaster.strength",
                value=dm_strength,
                note="Day master strength band.",
            )
        )

    favourable = elements.get("favourable") if isinstance(elements, dict) else None
    if isinstance(favourable, list):
        for element in favourable:
            if not isinstance(element, str):
                continue
            if element == "water":
                signal_id = "adaptability"
            elif element == "metal":
                signal_id = "structure_discipline"
            elif element == "earth":
                signal_id = "grounded_pragmatism"
            elif element == "fire":
                signal_id = "ambition_drive"
            else:
                signal_id = "creativity_expression"
            signals.append(
                _signal(
                    signal_id=signal_id,
                    domain="growth",
                    polarity="supporting",
                    strength=0.5,
                    system="chinese",
                    source="chinese.elements.favourable",
                    value=element,
                    note="Favourable element.",
                )
            )

    dominant = ten_gods.get("dominant") if isinstance(ten_gods, dict) else None
    if isinstance(dominant, list):
        for god in dominant:
            if not isinstance(god, str):
                continue
            if god in ("directOfficer", "sevenKillings"):
                signal_id = "structure_discipline"
            elif god in ("directWealth", "indirectWealth"):
                signal_id = "ambition_drive"
            elif god in ("directResource", "indirectResource"):
                signal_id = "learning_growth"
            elif god in ("eatingGod", "hurtingOfficer"):
                signal_id = "creativity_expression"
            else:
                signal_id = "independence_autonomy"
            signals.append(
                _signal(
                    signal_id=signal_id,
                    domain="career",
                    polarity="supporting",
                    strength=0.55,
                    system="chinese",
                    source="chinese.tenGods.dominant",
                    value=god,
                    note="Dominant ten god.",
                )
            )

    if isinstance(dm_element, str):
        signals.append(
            _signal(
                signal_id="identity_alignment",
                domain="personality",
                polarity="supporting",
                strength=0.4,
                system="chinese",
                source="chinese.dayMaster.element",
                value=dm_element,
                note="Day master element.",
            )
        )

    return signals


def extract_numerology_signals_v2(numerology: dict[str, Any]) -> list[CanonicalSignal]:
    signals: list[CanonicalSignal] = []
    primitives = numerology.get("primitives") if isinstance(numerology, dict) else None
    if not isinstance(primitives, dict):
        return signals

    life_path = primitives.get("life_path")
    if isinstance(life_path, dict):
        reduction = life_path.get("reduction")
        if isinstance(reduction, dict):
            value = reduction.get("final_value")
            if isinstance(value, int):
                if value in (1, 8):
                    signal_id = "ambition_drive"
                    domain = "career"
                elif value in (2, 6):
                    signal_id = "social_harmony"
                    domain = "relationships"
                elif value in (3, 5):
                    signal_id = "creativity_expression"
                    domain = "mind"
                elif value == 4:
                    signal_id = "structure_discipline"
                    domain = "growth"
                elif value == 7:
                    signal_id = "analytical_mind"
                    domain = "mind"
                elif value == 9:
                    signal_id = "service_orientation"
                    domain = "growth"
                else:
                    signal_id = "spiritual_intensity"
                    domain = "growth"
                signals.append(
                    _signal(
                        signal_id=signal_id,
                        domain=domain,
                        polarity="supporting",
                        strength=0.5,
                        system="numerology",
                        source="numerology.primitives.life_path",
                        value=value,
                        note="Life path number.",
                    )
                )

    return signals


def extract_signals_v2(systems: dict[str, Any]) -> list[CanonicalSignal]:
    signals: list[CanonicalSignal] = []
    western = systems.get("western", {}) if isinstance(systems, dict) else {}
    vedic = systems.get("vedic", {}) if isinstance(systems, dict) else {}
    chinese = systems.get("chinese", {}) if isinstance(systems, dict) else {}
    numerology = systems.get("numerology", {}) if isinstance(systems, dict) else {}

    signals.extend(extract_western_signals_v2(western))
    signals.extend(extract_vedic_signals_v2(vedic))
    signals.extend(extract_chinese_signals_v2(chinese))
    signals.extend(extract_numerology_signals_v2(numerology))

    def sort_key(sig: CanonicalSignal) -> tuple:
        evidence = sig.evidence[0]
        return (sig.id, evidence.system, evidence.source)

    return sorted(signals, key=sort_key)
