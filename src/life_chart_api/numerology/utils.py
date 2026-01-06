# src/life_chart_api/numerology/utils.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import re
import unicodedata


# -------------------------
# System parameters (Pythagorean)
# -------------------------

PYTHAGOREAN_MAP: Dict[str, int] = {
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

# Deterministic vowel policy for v1: Y is always treated as a vowel
VOWELS = set("AEIOUY")

MASTER_SET = {11, 22, 33}
KARMIC_DEBT_SET = {13, 14, 16, 19}


# -------------------------
# Data structures
# -------------------------

@dataclass(frozen=True)
class ReductionResult:
    start_value: int
    steps: List[int]
    final_value: int
    is_master: bool
    base_value: Optional[int] = None  # populated only if final_value is master and keep_masters=True


@dataclass(frozen=True)
class LetterValue:
    letter: str
    value: int


# -------------------------
# Normalisation
# -------------------------

_NON_AZ_RE = re.compile(r"[^A-Z]+")


def normalize_name(raw_name: str) -> str:
    """
    Normalise a name for numerology calculations:
      1) strip whitespace
      2) uppercase
      3) remove diacritics (NFKD, drop combining marks)
      4) keep A–Z only (strip spaces, punctuation, digits)
    """
    if raw_name is None:
        return ""

    s = raw_name.strip()
    if not s:
        return ""

    s = s.upper()

    # NFKD decomposition, then drop combining marks
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))

    # Keep only A–Z
    s = _NON_AZ_RE.sub("", s)
    return s


# -------------------------
# Core numeric helpers
# -------------------------

def _digit_sum(n: int) -> int:
    return sum(int(c) for c in str(abs(n)))


def reduce_number(n: int, keep_masters: bool = True) -> ReductionResult:
    """
    Reduce an integer by summing digits until:
      - single digit, OR
      - a master number (11/22/33) if keep_masters is True.

    If final is master and keep_masters=True, also compute base_value by fully reducing
    without master stops.
    """
    if not isinstance(n, int):
        raise TypeError(f"reduce_number expected int, got {type(n).__name__}")
    if n < 0:
        raise ValueError("reduce_number expected a non-negative integer")

    steps: List[int] = [n]
    cur = n

    while cur >= 10:
        if keep_masters and cur in MASTER_SET:
            break
        cur = _digit_sum(cur)
        steps.append(cur)

    is_master = cur in MASTER_SET
    base_value: Optional[int] = None

    if keep_masters and is_master:
        base = cur
        while base >= 10:
            base = _digit_sum(base)
        base_value = base

    return ReductionResult(
        start_value=n,
        steps=steps,
        final_value=cur,
        is_master=is_master,
        base_value=base_value,
    )


def letters_to_values(name_norm: str) -> List[LetterValue]:
    """
    Convert a normalised name (A–Z only) to mapped numeric values.
    Raises if it encounters unexpected characters (should not happen post-normalisation).
    """
    if not name_norm:
        return []

    out: List[LetterValue] = []
    for ch in name_norm:
        if ch not in PYTHAGOREAN_MAP:
            raise ValueError(f"Unexpected character after normalisation: {ch!r}")
        out.append(LetterValue(letter=ch, value=PYTHAGOREAN_MAP[ch]))
    return out


def sum_name(name_norm: str) -> int:
    return sum(lv.value for lv in letters_to_values(name_norm))


def sum_vowels(name_norm: str) -> int:
    return sum(lv.value for lv in letters_to_values(name_norm) if lv.letter in VOWELS)


def sum_consonants(name_norm: str) -> int:
    return sum(lv.value for lv in letters_to_values(name_norm) if lv.letter not in VOWELS)


# -------------------------
# Convenience: trace helpers
# -------------------------

def sum_name_with_trace(name_raw: str) -> Tuple[str, List[LetterValue], int]:
    """
    Returns (normalized_name, letter_values, total_sum).
    Useful for debug/smoke tests and building calculation traces later.
    """
    name_norm = normalize_name(name_raw)
    lvs = letters_to_values(name_norm)
    total = sum(lv.value for lv in lvs)
    return name_norm, lvs, total
