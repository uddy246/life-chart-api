from fastapi import FastAPI
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

import re
import swisseph as swe

app = FastAPI(title="Life Chart API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # temporary: allow all origins so the Lovable frontend can call the API
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# -------------------------
# Numerology (Pythagorean)
# -------------------------

# Pythagorean letter mapping
_PYTH_MAP = {
    **dict.fromkeys(list("AJS"), 1),
    **dict.fromkeys(list("BKT"), 2),
    **dict.fromkeys(list("CLU"), 3),
    **dict.fromkeys(list("DMV"), 4),
    **dict.fromkeys(list("ENW"), 5),
    **dict.fromkeys(list("FOX"), 6),
    **dict.fromkeys(list("GPY"), 7),
    **dict.fromkeys(list("HQZ"), 8),
    **dict.fromkeys(list("IR"), 9),
}

_VOWELS = set("AEIOUY")
_MASTER_NUMBERS = {11, 22, 33}


def _clean_name(name: str) -> str:
    # Keep letters only; uppercase
    if not name:
        return ""
    return re.sub(r"[^A-Za-z]", "", name).upper()


def _reduce_number(n: int, keep_master: bool = True) -> int:
    # Reduce to 1–9 unless master number (11/22/33)
    while n > 9:
        if keep_master and n in _MASTER_NUMBERS:
            return n
        digits = [int(d) for d in str(n)]
        n = sum(digits)
    return n


def _sum_letters(name_clean: str, mode: str) -> int:
    """
    mode:
      - "all": all letters
      - "vowels": vowels only
      - "consonants": consonants only
    """
    total = 0
    for ch in name_clean:
        is_vowel = ch in _VOWELS
        if mode == "vowels" and not is_vowel:
            continue
        if mode == "consonants" and is_vowel:
            continue
        total += _PYTH_MAP.get(ch, 0)
    return total


def numerology_from_name_and_dob(full_name: str, dob_str: str) -> dict:
    """
    Returns:
      - life_path
      - birthday
      - attitude
      - expression_destiny
      - maturity
      - soul_urge
      - personality
    """
    name_clean = _clean_name(full_name)

    # Parse DOB robustly (Lovable usually sends ISO: YYYY-MM-DD)
    dob = None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            dob = datetime.strptime(dob_str, fmt).date()
            break
        except Exception:
            continue

    if dob is None:
        # If DOB is missing or unparseable, return safe placeholders
        return {
            "life_path": None,
            "expression_destiny": _reduce_number(_sum_letters(name_clean, "all")) if name_clean else None,
            "soul_urge": _reduce_number(_sum_letters(name_clean, "vowels")) if name_clean else None,
            "personality": _reduce_number(_sum_letters(name_clean, "consonants")) if name_clean else None,
            "birthday": None,
        }

    # Life Path: reduce (YYYY + MM + DD) digits
    life_path_total = sum(int(d) for d in f"{dob.year:04d}{dob.month:02d}{dob.day:02d}")
    life_path = _reduce_number(life_path_total, keep_master=True)

    # Birthday number: reduce day of month
    birthday = _reduce_number(dob.day, keep_master=True)

    # Attitude number: reduce month + day
    attitude = _reduce_number(dob.month + dob.day, keep_master=True)

    # Name numbers
    expression_total = _sum_letters(name_clean, "all")
    soul_total = _sum_letters(name_clean, "vowels")
    personality_total = _sum_letters(name_clean, "consonants")

    expression_destiny = _reduce_number(expression_total, keep_master=True) if name_clean else None
    soul_urge = _reduce_number(soul_total, keep_master=True) if name_clean else None
    personality = _reduce_number(personality_total, keep_master=True) if name_clean else None

    maturity = (
        _reduce_number(life_path + expression_destiny, keep_master=True)
        if life_path is not None and expression_destiny is not None
        else None
    )

    return {
        "life_path": life_path,
        "expression_destiny": expression_destiny,
        "maturity": maturity,
        "soul_urge": soul_urge,
        "personality": personality,
        "birthday": birthday,
        "attitude": attitude,
    }


def _get_first(payload: dict, keys: list[str]) -> str | None:
    for k in keys:
        v = payload.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


_SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]


def _sign_from_longitude(lon: float) -> str:
    idx = int(lon // 30) % 12
    return _SIGNS[idx]


def compute_sun_signs(dob_str: str) -> tuple[str | None, str | None]:
    dob = None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            dob = datetime.strptime(dob_str, fmt).date()
            break
        except Exception:
            continue

    if dob is None:
        return (None, None)

    try:
        jd = swe.julday(dob.year, dob.month, dob.day, 12.0)
        lon = swe.calc_ut(jd, swe.SUN)[0][0]
        tropical = _sign_from_longitude(lon)

        swe.set_sid_mode(swe.SIDM_LAHIRI)
        ayan = swe.get_ayanamsa_ut(jd)
        sid_lon = (lon - ayan) % 360
        vedic = _sign_from_longitude(sid_lon)
    except Exception:
        return (None, None)

    return (tropical, vedic)


_CHINESE_ZODIAC = [
    "Rat",
    "Ox",
    "Tiger",
    "Rabbit",
    "Dragon",
    "Snake",
    "Horse",
    "Goat",
    "Monkey",
    "Rooster",
    "Dog",
    "Pig",
]


def compute_chinese_zodiac(dob_str: str) -> str | None:
    dob = None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            dob = datetime.strptime(dob_str, fmt).date()
            break
        except Exception:
            continue

    if dob is None:
        return None

    year = dob.year
    if (dob.month, dob.day) < (2, 4):
        year -= 1

    base_year = 2008
    idx = (year - base_year) % 12
    return _CHINESE_ZODIAC[idx]


@app.get("/health")
def health():
    return {"status": "ok"}

def render_profile_markdown(full_name: str, astrology: dict, numerology: dict) -> str:
    # Minimal v1 formatter: uses what we currently have, keeps bounded language where needed.
    # We will expand this to your full strict spec once the pipeline is proven.
    sun_tropical = astrology.get("western_sun_sign") or "Unknown"
    sun_sidereal = astrology.get("vedic_sun_sign") or "Unknown"
    chinese = astrology.get("chinese_zodiac") or "Unknown"

    life_path = numerology.get("life_path", "Unknown")
    birth_day = numerology.get("birthday", "Unknown")
    attitude = numerology.get("attitude", "Unknown")
    expression = numerology.get("expression_destiny", "Unknown")
    soul_urge = numerology.get("soul_urge", "Unknown")
    personality = numerology.get("personality", "Unknown")
    maturity = numerology.get("maturity", "Unknown")

    return f"""# PROFILE: **{full_name or "Unknown"}**

---

## ASTROLOGY

---

### A. Western Astrology (Tropical)

#### Sun: **{sun_tropical}**
- Core identity: High-confidence interpretation based on Sun sign only.
- Strength expression: Likely strengths aligned with {sun_tropical} themes.
- Friction points: Common {sun_tropical} pitfalls under stress.
- Time-of-day influence: Not assessed without confirmed Moon/Ascendant.

---

### B. Vedic Astrology (Sidereal)

#### Sun: **{sun_sidereal}**
- Core orientation: High-confidence interpretation based on sidereal Sun sign only.
- Strength expression: Likely strengths aligned with {sun_sidereal} themes.
- Friction points: Common {sun_sidereal} pitfalls under stress.

---

#### Lunar Nakshatra + Pada (Vedic)
**High-likelihood Nakshatra:** **Not yet computed**
**Likely Pada band:** **Not yet computed**
- Bounded interpretation will be added once nakshatra computation is implemented.

---

### C. Chinese Astrology  
*(Vietnamese zodiac is included here, as it is structurally the same system)*

#### Chinese Zodiac: **{chinese}**
- Temperament/strategy: High-confidence interpretation based on year animal only.
- Shadow tendencies: Common challenges associated with {chinese} patterns.

---

#### C1. BaZi (Four Pillars of Destiny) - *Chinese Astrology Subsystem*
**Day Master (Core Self):** **Not yet computed**
- Pillars/day master will be added once BaZi computation is implemented.

---

### ASTROLOGICAL CONVERGENT SUMMARY
- Not yet computed (requires multi-system trait extraction and overlap logic).

---

## NUMEROLOGY

### Life Path Number: **{life_path}**
- Themes: High-confidence themes based on Life Path.
- Risks: Typical overuse/underuse patterns for this number.

### Birth Day Number: **{birth_day}**
- Supports the Life Path with more specific behavioural tendencies.

### Attitude Number: **{attitude}**
- Derived from DOB (month + day); reflects the immediate "first impression" style.

### Expression / Destiny Number: **{expression}**
- Themes: High-confidence themes based on name-derived total.

### Soul Urge / Heart's Desire: **{soul_urge}**
- Motivational drivers inferred from vowel total.

### Personality Number: **{personality}**
- Social presentation inferred from consonant total.

### Maturity Number: **{maturity}**
- Derived from Life Path + Expression; reflects the longer-term direction of development.

---

### NUMEROLOGICAL CONCLUSION
Numerology is partially computed (core numbers are present). Additional numbers will be added next to complete the profile.

---

## COMBINED ASTROLOGY + NUMEROLOGY SUMMARY
- Not yet computed (requires overlap logic across systems and numerology themes).

---

## FINAL CONCLUSION  
### **Archetype: *Not yet assigned***
This profile is currently based on a subset of computed factors. Once the remaining systems are computed, the archetype and convergent summaries will be generated consistently.
"""


@app.post("/profile/compute")
def compute_profile(payload: dict):
    # Try to extract the user's name and DOB from whatever Lovable sends
    full_name = _get_first(payload, ["full_name", "name", "fullname", "fullName"]) or ""
    dob_str = _get_first(payload, ["dob", "date_of_birth", "birth_date", "birthDate", "date"]) or ""

    # Compute real numerology
    numerology = numerology_from_name_and_dob(full_name, dob_str)

    trop, ved = compute_sun_signs(dob_str)
    cz = compute_chinese_zodiac(dob_str)
    astrology = {
        "western_sun_sign": trop,
        "vedic_sun_sign": ved,
        "chinese_zodiac": cz,
        "lunar_nakshatra": None,
        "lunar_pada": None,
        "bazi_day_master": None,
        "bazi_pillars": None,
    }

    profile_markdown = render_profile_markdown(full_name, astrology, numerology)

    return {
        "astrology": astrology,
        "numerology": numerology,
        "profile_markdown": profile_markdown,
        "unified_overlapping_traits": [
            {
                "title": "Intuitive",
                "description": "You often sense patterns before they fully appear and trust your inner guidance.",
                "supported_by": ["Astrology", "Numerology"]
            },
            {
                "title": "Compassionate",
                "description": "You naturally empathize with others and are drawn to helping roles.",
                "supported_by": ["Astrology"]
            },
            {
                "title": "Inspirational",
                "description": "You motivate others through insight, presence, and perspective.",
                "supported_by": ["Numerology"]
            }
        ]
    }
