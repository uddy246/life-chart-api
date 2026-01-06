from __future__ import annotations

from typing import Any, Dict, List, Optional

from life_chart_api.numerology.compute import PrimitiveResult

LAYER_LABELS: Dict[int, str] = {
    1: "Emotional / Experiential",
    2: "Behavioural / Pressure",
    3: "Structural / Life trajectory",
    4: "Integration / Maturity",
}

PRIMITIVE_LAYER: Dict[str, int] = {
    "life_path": 3,
    "expression": 1,
    "soul_urge": 1,
    "personality": 1,
    "birthday": 2,
    "attitude": 2,
    "maturity": 4,
    "personal_year": 3,
}

INTERPRETATION_TABLE: Dict[int, Dict[int, Dict[str, List[str]]]] = {
    1: {
        1: {
            "functions": ["emotional_processing", "relational_needs"],
            "healthy": [
                "moves from impulse to clear desire and chooses a first step",
                "creates self-definition by making a small, concrete start",
            ],
            "stress": [
                "tightens into self-protection and isolates to avoid interference",
                "pushes for unilateral control when feedback appears",
            ],
            "integration": [
                "keeps agency while inviting collaboration on the next step",
                "holds a steady direction without collapsing into rigidity",
            ],
        },
        2: {
            "functions": ["decision_making_under_pressure", "boundaries_and_assertion"],
            "healthy": [
                "tracks the emotional field and adapts without losing position",
                "builds alignment by pacing decisions with others",
            ],
            "stress": [
                "over-weights harmony and delays necessary moves",
                "absorbs tension and becomes reactive to others' needs",
            ],
            "integration": [
                "balances receptivity with a clear boundary of choice",
                "uses sensitivity as input rather than as a command",
            ],
        },
        3: {
            "functions": ["growth_lesson_theme", "discipline_and_responsibility"],
            "healthy": [
                "translates inner experience into shareable signals",
                "creates momentum by reframing problems into options",
            ],
            "stress": [
                "scatters energy across too many channels",
                "performs for validation and loses coherence",
            ],
            "integration": [
                "grounds expression in a single through-line",
                "uses play to recover clarity, not to avoid it",
            ],
        },
        4: {
            "functions": ["integration_outcome"],
            "healthy": [
                "turns intent into reliable routines and sequence",
                "builds trust by showing up predictably",
            ],
            "stress": [
                "locks into rigidity and resists iteration",
                "confuses safety with control and slows change",
            ],
            "integration": [
                "keeps structure flexible while protecting core commitments",
                "uses discipline to support, not suppress, adaptation",
            ],
        },
    },
    2: {
        1: {
            "functions": ["emotional_processing", "relational_needs"],
            "healthy": [
                "stays close enough to feel others while staying present to self",
                "creates safety by reflecting back what is felt",
            ],
            "stress": [
                "merges to keep peace and loses clarity",
                "hesitates to assert needs and builds quiet resentment",
            ],
            "integration": [
                "offers attunement without abandoning personal limits",
                "allows difference to exist without rupturing bond",
            ],
        },
        2: {
            "functions": ["decision_making_under_pressure", "conflict_response"],
            "healthy": [
                "regulates conflict by holding opposing needs in view",
                "slows the pace so cooperation can form",
            ],
            "stress": [
                "avoids decisive action to keep equilibrium",
                "over-adjusts to volatility and loses orientation",
            ],
            "integration": [
                "chooses a side when needed while staying relational",
                "uses patience to shape outcomes, not to defer them",
            ],
        },
        3: {
            "functions": ["growth_lesson_theme", "discipline_and_responsibility"],
            "healthy": [
                "connects people and resources to keep momentum stable",
                "builds bridges that reduce friction over time",
            ],
            "stress": [
                "prioritizes connection at the expense of direction",
                "spreads attention thin to avoid disappointing others",
            ],
            "integration": [
                "maintains connection while protecting strategic focus",
                "uses cooperation to amplify, not dilute, outcomes",
            ],
        },
        4: {
            "functions": ["integration_outcome"],
            "healthy": [
                "keeps systems steady by tending the weak points",
                "restores trust by repairing small ruptures quickly",
            ],
            "stress": [
                "becomes over-cautious and resists necessary shifts",
                "takes on too much maintenance and burns out",
            ],
            "integration": [
                "distributes care to keep stability sustainable",
                "lets systems flex without collapsing safety",
            ],
        },
    },
    3: {
        1: {
            "functions": ["emotional_processing", "communication_expression"],
            "healthy": [
                "uses emotion to energize exploration and learning",
                "marks feelings with words that invite response",
            ],
            "stress": [
                "seeks stimulation to avoid discomfort",
                "over-amplifies expression to force engagement",
            ],
            "integration": [
                "channels excitement into a focused message",
                "allows joy to organize rather than distract",
            ],
        },
        2: {
            "functions": ["decision_making_under_pressure", "boundaries_and_assertion"],
            "healthy": [
                "keeps morale high by translating tension into movement",
                "adapts quickly without losing authenticity",
            ],
            "stress": [
                "over-performs and disconnects from the core need",
                "moves too fast and skips essential follow-through",
            ],
            "integration": [
                "uses improvisation to open choices, then commits",
                "stays expressive while honoring boundaries",
            ],
        },
        3: {
            "functions": ["growth_lesson_theme", "discipline_and_responsibility"],
            "healthy": [
                "creates long-term momentum through optimism and clarity",
                "reframes setbacks into learning cycles",
            ],
            "stress": [
                "spreads attention across too many narratives",
                "trades depth for breadth and loses direction",
            ],
            "integration": [
                "anchors communication in a consistent message",
                "uses creativity to reinforce strategy",
            ],
        },
        4: {
            "functions": ["integration_outcome"],
            "healthy": [
                "builds a stable voice that others can rely on",
                "uses storytelling to transmit hard-won lessons",
            ],
            "stress": [
                "avoids commitment to keep options open",
                "treats meaning as entertainment and erodes trust",
            ],
            "integration": [
                "commits to a message and refines it over time",
                "uses play to deepen, not dilute, integrity",
            ],
        },
    },
    4: {
        1: {
            "functions": ["emotional_processing", "relational_needs"],
            "healthy": [
                "slows emotion into practical steps",
                "creates calm by reducing complexity",
            ],
            "stress": [
                "hardens into control to manage uncertainty",
                "dismisses feelings as inefficiency",
            ],
            "integration": [
                "uses structure to protect feeling without stifling it",
                "keeps order in service of growth",
            ],
        },
        2: {
            "functions": ["decision_making_under_pressure", "boundaries_and_assertion"],
            "healthy": [
                "creates dependable routines under pressure",
                "builds safety through consistent follow-through",
            ],
            "stress": [
                "gets stuck in procedure even when outcomes suffer",
                "uses rigidity to avoid change",
            ],
            "integration": [
                "adapts systems while preserving their purpose",
                "keeps standards high without becoming inflexible",
            ],
        },
        3: {
            "functions": ["growth_lesson_theme", "discipline_and_responsibility"],
            "healthy": [
                "turns goals into durable structures over time",
                "commits to patient execution and steady growth",
            ],
            "stress": [
                "over-values certainty and resists experimentation",
                "equates stability with stagnation",
            ],
            "integration": [
                "uses constraints to increase long-term resilience",
                "keeps trajectory steady while allowing iteration",
            ],
        },
        4: {
            "functions": ["integration_outcome"],
            "healthy": [
                "anchors maturity in reliable systems and habits",
                "becomes a stabilizing presence in complex contexts",
            ],
            "stress": [
                "over-identifies with duty and loses vitality",
                "confuses endurance with effectiveness",
            ],
            "integration": [
                "balances responsibility with renewal",
                "keeps structure alive through periodic recalibration",
            ],
        },
    },
    5: {
        1: {
            "functions": ["emotional_processing", "relational_needs"],
            "healthy": [
                "lets feelings signal when a shift is needed",
                "creates options instead of forcing certainty",
            ],
            "stress": [
                "reacts impulsively to discomfort",
                "avoids depth by chasing novelty",
            ],
            "integration": [
                "uses freedom to choose a better process",
                "moves with change without losing direction",
            ],
        },
        2: {
            "functions": ["decision_making_under_pressure", "conflict_response"],
            "healthy": [
                "stays flexible while keeping core intent",
                "tests small moves before committing fully",
            ],
            "stress": [
                "keeps shifting to avoid accountability",
                "creates instability that magnifies pressure",
            ],
            "integration": [
                "sets guardrails so change remains productive",
                "uses experimentation to reveal a sustainable path",
            ],
        },
        3: {
            "functions": ["growth_lesson_theme", "freedom_vs_structure_tension"],
            "healthy": [
                "keeps life course responsive to emerging information",
                "opens new paths without abandoning the whole plan",
            ],
            "stress": [
                "changes course too often and loses momentum",
                "over-corrects in reaction to uncertainty",
            ],
            "integration": [
                "integrates variety into a coherent trajectory",
                "builds freedom into structure over time",
            ],
        },
        4: {
            "functions": ["integration_outcome"],
            "healthy": [
                "builds a life that can flex without breaking",
                "creates routines that protect autonomy",
            ],
            "stress": [
                "rejects commitments and destabilizes long-term goals",
                "treats freedom as escape from maturation",
            ],
            "integration": [
                "turns adaptability into a stable identity",
                "matures into freedom with responsibility",
            ],
        },
    },
    11: {
        1: {
            "functions": ["emotional_processing", "relational_needs"],
            "healthy": [
                "registers subtle shifts and translates them into clarity",
                "uses intensity to orient toward purpose",
            ],
            "stress": [
                "overloads and becomes hyper-reactive",
                "mistakes intensity for certainty and polarizes quickly",
            ],
            "integration": [
                "holds sensitivity without being ruled by it",
                "lets insight move into grounded action",
            ],
        },
        2: {
            "functions": ["decision_making_under_pressure", "conflict_response"],
            "healthy": [
                "uses pressure as a signal to refine direction",
                "amplifies cooperation by articulating the deeper aim",
            ],
            "stress": [
                "swings between idealism and shutdown",
                "absorbs noise and loses the signal",
            ],
            "integration": [
                "filters pressure into a clear, usable message",
                "keeps vision stable while engaging reality",
            ],
        },
        3: {
            "functions": ["growth_lesson_theme", "discipline_and_responsibility"],
            "healthy": [
                "orients long-term choices around a guiding signal",
                "creates meaning that organizes direction",
            ],
            "stress": [
                "chases the perfect path and stalls progress",
                "over-idealizes the mission and ignores constraints",
            ],
            "integration": [
                "grounds inspiration in iterative execution",
                "keeps trajectory aligned without becoming rigid",
            ],
        },
        4: {
            "functions": ["integration_outcome"],
            "healthy": [
                "turns insight into reliable structures others can use",
                "models integrity between inner signal and outer form",
            ],
            "stress": [
                "burns out trying to hold the full intensity alone",
                "retreats into isolation when systems resist change",
            ],
            "integration": [
                "shares the load and builds sustainable pathways",
                "stabilizes insight through disciplined practice",
            ],
        },
    },
}


def _layer_for_key(key: str) -> int:
    return PRIMITIVE_LAYER.get(key, 2)


def _get_table_entry(number: int, layer: int) -> Dict[str, List[str]]:
    default_functions = {
        1: ["emotional_processing", "relational_needs"],
        2: ["decision_making_under_pressure", "boundaries_and_assertion"],
        3: ["growth_lesson_theme", "discipline_and_responsibility"],
        4: ["integration_outcome"],
    }
    if number in INTERPRETATION_TABLE:
        by_layer = INTERPRETATION_TABLE[number]
        if layer in by_layer:
            return by_layer[layer]
    return {
        "functions": list(default_functions.get(layer, ["growth_lesson_theme"])),
        "healthy": [
            "organizes attention into a workable process",
        ],
        "stress": [
            "over-controls the process and narrows options",
        ],
        "integration": [
            "keeps the process stable while allowing learning",
        ],
    }


def _growth_tension(number: int, base_number: Optional[int]) -> List[Dict[str, Any]]:
    if base_number is None:
        return [{"type": "practice", "message": "stabilizes growth through consistent practice"}]
    return [
        {
            "type": "master_to_base",
            "master": number,
            "base": base_number,
            "message": "Intensity must be stabilised through the base expression.",
        }
    ]


def generate_signals(primitives: Dict[str, PrimitiveResult]) -> List[Dict[str, Any]]:
    signals: List[Dict[str, Any]] = []
    for key, primitive in primitives.items():
        number = primitive.reduction.final_value
        base_number = primitive.reduction.base_value if primitive.reduction.is_master else None
        layer = _layer_for_key(key)
        table_entry = _get_table_entry(number, layer)
        signal = {
            "signal_id": f"{key}:{number}:{layer}",
            "source_key": key,
            "number": number,
            "base_number": base_number,
            "primary_layer": layer,
            "functions": list(table_entry["functions"]),
            "healthy_expression": list(table_entry["healthy"]),
            "stress_expression": list(table_entry["stress"]),
            "growth_tension": _growth_tension(number, base_number),
        }
        signals.append(signal)
    return signals


def generate_claims(primitives: Dict[str, PrimitiveResult]) -> List[Dict[str, Any]]:
    claims: List[Dict[str, Any]] = []
    signals = generate_signals(primitives)
    for signal in signals:
        layer = signal["primary_layer"]
        prefix = {
            1: "When safe,",
            2: "Under pressure,",
            3: "Over time life tends to",
            4: "With maturity you stabilise into",
        }[layer]
        if layer == 1:
            phrase = signal["healthy_expression"][0]
        elif layer == 2:
            phrase = signal["stress_expression"][0]
        elif layer == 3:
            phrase = signal["healthy_expression"][0]
        else:
            master_msg = next(
                (
                    item.get("message")
                    for item in signal["growth_tension"]
                    if item.get("type") == "master_to_base"
                ),
                None,
            )
            if master_msg:
                phrase = master_msg
            else:
                entry = _get_table_entry(signal["number"], layer)
                phrase = entry["integration"][0]
        claim = {
            "layer": layer,
            "layer_label": LAYER_LABELS[layer],
            "text": f"{prefix} {phrase}.",
            "evidence": [{"source_key": signal["source_key"], "number": signal["number"]}],
        }
        claims.append(claim)
    return claims
