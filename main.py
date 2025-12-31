from fastapi import FastAPI
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

import re

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
      - expression_destiny
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

    # Name numbers
    expression_total = _sum_letters(name_clean, "all")
    soul_total = _sum_letters(name_clean, "vowels")
    personality_total = _sum_letters(name_clean, "consonants")

    expression_destiny = _reduce_number(expression_total, keep_master=True) if name_clean else None
    soul_urge = _reduce_number(soul_total, keep_master=True) if name_clean else None
    personality = _reduce_number(personality_total, keep_master=True) if name_clean else None

    return {
        "life_path": life_path,
        "expression_destiny": expression_destiny,
        "soul_urge": soul_urge,
        "personality": personality,
        "birthday": birthday,
    }


def _get_first(payload: dict, keys: list[str]) -> str | None:
    for k in keys:
        v = payload.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/profile/compute")
def compute_profile(payload: dict):
    # Try to extract the user's name and DOB from whatever Lovable sends
    full_name = _get_first(payload, ["full_name", "name", "fullname", "fullName"]) or ""
    dob_str = _get_first(payload, ["dob", "date_of_birth", "birth_date", "birthDate", "date"]) or ""

    # Compute real numerology
    numerology = numerology_from_name_and_dob(full_name, dob_str)

    # Keep astrology placeholders for now (unchanged)
    return {
        "astrology": {
            "western_sun_sign": "Pisces",
            "vedic_sun_sign": "Aquarius",
            "chinese_zodiac": "Dragon",
            "celtic_tree_sign": "Ash",
            "mayan_zodiac": "Jaguar"
        },
        "numerology": numerology,
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
