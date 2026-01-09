from __future__ import annotations

CANONICAL_TAGS: list[str] = [
    "ambition_status",
    "communication_social",
    "creativity_expression",
    "discipline_structure",
    "emotion_sensitivity",
    "independence_autonomy",
    "learning_growth",
    "relationships_harmony",
    "risk_change",
    "service_duty",
    "spirituality_intuition",
    "stability_security",
]

TAG_KEYWORDS: dict[str, list[str]] = {
    "ambition_status": ["ambition", "status", "leadership", "achievement", "career", "prestige"],
    "communication_social": ["communication", "social", "network", "collaboration", "community", "dialogue"],
    "creativity_expression": ["creative", "expression", "art", "original", "imagination", "inspiration"],
    "discipline_structure": ["discipline", "structure", "responsibility", "order", "routine", "duty"],
    "emotion_sensitivity": ["emotion", "sensitive", "empathy", "feeling", "vulnerable", "tender"],
    "independence_autonomy": ["independent", "autonomy", "freedom", "self-directed", "sovereign", "initiative"],
    "learning_growth": ["learning", "growth", "study", "development", "curiosity", "expansion"],
    "relationships_harmony": ["relationship", "harmony", "bond", "partnership", "connection", "intimacy"],
    "risk_change": ["risk", "change", "transition", "shift", "volatility", "uncertainty"],
    "service_duty": ["service", "duty", "support", "care", "help", "responsibility"],
    "spirituality_intuition": ["spiritual", "intuition", "inner", "soul", "meaning", "transcend"],
    "stability_security": ["stability", "security", "grounded", "steady", "consistency", "safety"],
}
