# Numerology Engine Specification (Pythagorean) — v1.0

## 0) Purpose and Design Principles

### Purpose
Compute numerology primitives from **DOB** and **birth name**, interpret them using a **four-layer model**, and emit output in a canonical schema designed for **cross-system fusion** with astrology.

### Non-negotiable principles
1. **Separate math from meaning**  
   Computations are deterministic; interpretations are declarative mappings.
2. **Tension is first-class**  
   Do not flatten master numbers or karmic debt into a single digit without preserving tension.
3. **Layer-scoped claims only**  
   Every claim is assigned to exactly one layer (L1–L4). Do not mix layers in a single statement.
4. **Fusion-ready output**  
   Emit “claims” using `layer + function` so astrology engines can align without vague trait overlap.

---

## 1) Inputs

### Required
- `full_name_birth`: string  
- `dob`: string (ISO `YYYY-MM-DD`)

### Optional (Forecast)
- `as_of_date`: string (ISO). Default: server “today”.
- `forecast_year`: int (if you want Personal Year for a specific year)

---

## 2) Normalisation Rules

### Name normalisation: `normalize_name(raw_name) -> str`
Apply in order:
1. Trim whitespace
2. Uppercase
3. Remove diacritics (NFKD → strip combining marks)
4. Keep letters A–Z only (strip spaces, punctuation, hyphens, apostrophes, digits)

Output is the canonical name string used for all letter mapping.

### Vowel policy (must be explicit and consistent)
Default (recommended for determinism):
- Vowels: `A E I O U Y` (Y always treated as vowel)

---

## 3) System Parameters (Pythagorean)

### Letter → Number mapping (1–9)
- 1: A J S  
- 2: B K T  
- 3: C L U  
- 4: D M V  
- 5: E N W  
- 6: F O X  
- 7: G P Y  
- 8: H Q Z  
- 9: I R  

### Master numbers
- `MASTER_SET = {11, 22, 33}`

### Karmic debt numbers (flags)
- `KARMIC_DEBT_SET = {13, 14, 16, 19}`

---

## 4) Core Utility Functions

### 4.1 `reduce_number(n: int, keep_masters: bool = True) -> ReductionResult`

**Inputs**
- `n`: integer ≥ 0
- `keep_masters`: if True, stop reduction at 11/22/33

**Algorithm**
- While `n` has more than 1 digit:
  - If `keep_masters` and `n` in MASTER_SET: stop
  - Replace `n` with sum of digits of `n`
- Return:
  - `final_value`: n
  - `steps`: list of intermediate values, including start and final
  - `is_master`: True iff `final_value` in MASTER_SET
  - `base_value`: if final is master, also compute full reduction without master stops (11→2, 22→4, 33→6)

**Example**
- 38 → 11 (master) with base_value 2

### 4.2 `letters_to_values(name_norm: str) -> list[int]`
Map each letter to 1–9 using mapping.

### 4.3 `sum_name(name_norm: str) -> int`
Sum all mapped values.

### 4.4 `sum_vowels(name_norm: str) -> int`
Sum mapped values where char in VOWELS.

### 4.5 `sum_consonants(name_norm: str) -> int`
Sum mapped values where char not in VOWELS.

### 4.6 `dob_digits(dob: date) -> list[int]`
Return digit list of `YYYYMMDD` (this spec uses YYYYMMDD).

---

## 5) Computation Methods (Deterministic Definitions)

### 5.1 Life Path
**Method (locked):** `digit_sum_full_date_YYYYMMDD`
- Convert DOB to digits in `YYYYMMDD`
- Sum digits → reduce with master preservation

Return:
- `value` (possibly master)
- `base_value` (if master)
- trace with digit list and sums

### 5.2 Expression / Destiny
- `sum_name(name_norm)` → reduce with master preservation

### 5.3 Soul Urge / Heart’s Desire
- `sum_vowels(name_norm)` → reduce with master preservation

### 5.4 Personality
- `sum_consonants(name_norm)` → reduce with master preservation

### 5.5 Birthday Number
- Day of month (e.g., 26) → reduce with master preservation

### 5.6 Attitude Number
- Month + Day → reduce with master preservation

### 5.7 Maturity Number
- Reduce( LifePath.value + Expression.value ) with master preservation  
  (Use displayed values; preserve tension separately.)

### 5.8 Personal Year (Temporal)
**Definition**
- Reduce( birth_month + birth_day + digit_sum(target_year) )

**Policy decision (locked for v1):**
- `keep_masters_personal_year = False` (forecasting layer is cleaner without masters)

Also compute:
- Personal Month: reduce(PersonalYear + month)
- Personal Day: reduce(PersonalMonth + day)

---

## 6) Output: Canonical Engine Response Schema

Return a single JSON object containing:

### 6.1 `system_meta`
- `system`: `"numerology"`
- `variant`: `"pythagorean"`
- `version`: `"1.0"`
- `policies`:
  - `vowels`: `"AEIOUY_ALWAYS"`
  - `life_path_method`: `"YYYYMMDD_DIGIT_SUM"`
  - `masters`: `[11,22,33]`
  - `karmic_debts`: `[13,14,16,19]`
  - `keep_masters_personal_year`: `false`

### 6.2 `inputs`
- `dob`
- `full_name_birth_raw`
- `full_name_birth_normalized`
- `as_of_date` (resolved)
- `forecast_year` (resolved if used)

### 6.3 `primitives` (math-only results)
Each primitive object includes:
- `key`: e.g. `"life_path"`
- `raw_sum` or `raw_components`
- `reduction`: { `steps`, `final_value`, `is_master`, `base_value?` }
- `flags`: { `karmic_debt?`: bool, `master?`: bool }

Primitives to include in v1:
- `life_path`
- `expression`
- `soul_urge`
- `personality`
- `birthday`
- `attitude`
- `maturity`
- `personal_year` (+ optional `personal_month`, `personal_day`)

### 6.4 `signals` (interpretation-ready units)
One signal per primitive (+ derived tension signals). Each includes:
- `signal_id`
- `source_key`
- `number`: final_value
- `base_number` (if master)
- `primary_layer` (1–4)
- `layer_affinity` (optional weights)
- `functions`: list of functional tags
- `healthy_expression`: list
- `stress_expression`: list
- `growth_tension`: list of tension objects

### 6.5 `claims` (layer-scoped statements)
Claims are the fusion unit.

Each claim:
- `claim_id`
- `layer`: 1|2|3|4
- `function`: canonical function tag
- `text`: string
- `evidence`: list of `{source_key, number, aspect}` references
- `confidence`: 0–1 (optional heuristic)

### 6.6 `synthesis` (structured narrative)
Layer-separated sections:
- `emotional_defaults` (L1)
- `pressure_behavior` (L2)
- `life_demands` (L3)
- `integration_path` (L4)
- `current_cycle_emphasis` (Personal Year; temporal)

---

## 7) Canonical “Function” Tags (for Cross-Referencing)

Start set (expand later):
- `emotional_processing`
- `relational_needs`
- `communication_expression`
- `identity_presentation`
- `decision_making_under_pressure`
- `conflict_response`
- `boundaries_and_assertion`
- `authority_relationship`
- `discipline_and_responsibility`
- `freedom_vs_structure_tension`
- `growth_lesson_theme`
- `integration_outcome`
- `cycle_emphasis`

Each numerology signal should map to 1–3 functions.

---

## 8) Layer Mapping Rules (Default)

- Soul Urge → L1 primary; functions: emotional_processing, relational_needs  
- Personality → L1 primary; functions: identity_presentation, communication_expression  
- Expression → L1 primary, L4 secondary; functions: communication_expression, integration_outcome  
- Birthday → L2 primary; functions: decision_making_under_pressure, boundaries_and_assertion  
- Attitude → L2 primary; functions: authority_relationship, conflict_response  
- Life Path (full) → L3 primary, L2 secondary; functions: growth_lesson_theme, discipline_and_responsibility  
- Life Path base (if master) → L1 secondary; functions: emotional_processing  
- Maturity → L4 primary; functions: integration_outcome  
- Personal Year → L3 primary (temporal); functions: cycle_emphasis

---

## 9) Tension Model

### 9.1 Master-to-base tension
If a primitive reduces to master (11/22/33):
- `type`: `"master_to_base"`
- `master`: 11|22|33
- `base`: 2|4|6
- `message`: “Intensity must be stabilised through the base expression.”

### 9.2 Karmic debt tension
If any raw sum equals a karmic debt number OR an intermediate reduction step hits it (rule locked for v1: raw sum OR intermediate step):
- `type`: `"karmic_debt"`
- `number`: 13|14|16|19
- `message`: life-lesson constraint statement (number-specific table)

### 9.3 Recurrent polarity tension (optional v2)
Detect repeated clashes (e.g., dominant 5 vs dominant 4) and emit:
- `type`: `"polarity"`
- `pair`: `"5_vs_4"`
- `message`: freedom vs structure tension narrative

---

## 10) Interpretation Tables (Implementation Guidance)

Implement meaning as declarative dictionaries, not hard-coded prose:
- `INTERPRETATION[number][layer] = {functions, healthy, stress, integration}`

This enables consistent language, tuning, and localisation.

---

## 11) Composition Rules (Claims Generator)

1. Generate claims in order L1 → L2 → L3 → L4 → Cycle.
2. Each claim must cite evidence from at least one signal.
3. Never mix layers in a single claim.
4. Prefer process framing:
   - L1: “When safe…”
   - L2: “Under pressure…”
   - L3: “Over time life tends to…”
   - L4: “With maturity you stabilise into…”
   - Cycle: “This year emphasises…”

Recommended quantity:
- L1: 3–5 claims
- L2: 3–5 claims
- L3: 3–5 claims
- L4: 2–4 claims
- Cycle: 2–3 claims

---

## 12) API Endpoint Contract (Suggested)

### `POST /numerology/compute`
**Body**
- `dob`
- `full_name_birth`
- `as_of_date` optional
- `forecast_year` optional

**Response**
- full schema object described above (`system_meta`, `inputs`, `primitives`, `signals`, `claims`, `synthesis`)
