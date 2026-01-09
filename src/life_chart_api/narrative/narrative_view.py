from __future__ import annotations

from collections import Counter
from typing import Any

_THEME_LABELS = {
    "structure_discipline": "structure and discipline",
    "expansion_growth": "growth and expansion",
    "pressure_maturation": "pressure and maturation",
    "love_harmony": "relationships and harmony",
    "volatility_ambition": "volatility and ambition",
}

_CAREER_TAGS = {"structure_discipline", "authority", "ambition", "responsibility", "pressure_maturation"}
_RELATIONSHIP_TAGS = {"love_harmony", "relationships", "belonging"}

_TEMPLATES = {
    "neutral": {
        "overview_headline": "Next period highlights {theme} with {polarity} emphasis.",
        "window_title": {
            "supporting": "Supportive window for {theme}",
            "challenging": "Challenging window: {theme}",
            "neutral": "Mixed window: {theme}",
        },
        "frame": (
            "From {start} to {end}, this is a {polarity} period with intensity {intensity:.2f} "
            "and confidence {confidence:.2f}."
        ),
        "theme_focus": "Primary focus: {themes}.",
        "alignment": "Signals align across {count} systems ({systems}).",
        "takeaways": {
            "supporting": [
                "Lean into {theme} actions; aim for steady execution.",
                "Prioritize decisions that compound over weeks, not days.",
            ],
            "challenging": [
                "Treat {theme} as a constraint; reduce overextension.",
                "Favor consolidation and risk management.",
            ],
            "neutral": [
                "Use this period for calibration and small experiments.",
                "Watch for mixed signals; avoid irreversible commitments.",
            ],
        },
        "domain_headline": {
            "default": "Key {domain} themes in this range",
            "empty": "No strong {domain} windows in this range.",
        },
        "domain_bullet": "{start} to {end}: {polarity} focus on {theme}.",
        "domain_empty": ["No high-confidence windows in this domain.", "Monitor for emerging signals."],
        "domain_fallback": "Monitor for emerging signals.",
    },
    "direct": {
        "overview_headline": "Next period: {polarity} focus on {theme}.",
        "window_title": {
            "supporting": "Supportive: {theme}",
            "challenging": "Challenging: {theme}",
            "neutral": "Mixed: {theme}",
        },
        "frame": "{start}–{end}: {polarity}. Intensity {intensity:.2f}, confidence {confidence:.2f}.",
        "theme_focus": "Focus: {themes}.",
        "alignment": "Aligned across {count} systems ({systems}).",
        "takeaways": {
            "supporting": [
                "Act on {theme} with steady execution.",
                "Favor compounding progress over quick wins.",
            ],
            "challenging": [
                "Limit overreach around {theme}.",
                "Consolidate and manage risk.",
            ],
            "neutral": [
                "Keep moves small and reversible.",
                "Track signals before committing.",
            ],
        },
        "domain_headline": {
            "default": "{domain} focus in this range",
            "empty": "No strong {domain} windows in this range.",
        },
        "domain_bullet": "{start}–{end}: {polarity} focus on {theme}.",
        "domain_empty": ["No high-confidence windows in this domain.", "Monitor for emerging signals."],
        "domain_fallback": "Monitor for emerging signals.",
    },
    "reflective": {
        "overview_headline": "Next period shows {theme} with a {polarity} tilt.",
        "window_title": {
            "supporting": "Supportive window for {theme}",
            "challenging": "Challenging window around {theme}",
            "neutral": "Mixed window around {theme}",
        },
        "frame": (
            "{start} to {end} shows a {polarity} emphasis with intensity {intensity:.2f} "
            "and confidence {confidence:.2f}."
        ),
        "theme_focus": "Primary focus: {themes}.",
        "alignment": "Signals align across {count} systems ({systems}).",
        "takeaways": {
            "supporting": [
                "Consider leaning into {theme} with steady pacing.",
                "Favor choices that build over weeks.",
            ],
            "challenging": [
                "Consider {theme} as a constraint and scale back.",
                "Emphasize consolidation and caution.",
            ],
            "neutral": [
                "Use the time for calibration and small experiments.",
                "Notice mixed signals before larger commitments.",
            ],
        },
        "domain_headline": {
            "default": "Key {domain} themes in this range",
            "empty": "No strong {domain} windows in this range.",
        },
        "domain_bullet": "{start} to {end}: {polarity} focus on {theme}.",
        "domain_empty": ["No high-confidence windows in this domain.", "Monitor for emerging signals."],
        "domain_fallback": "Monitor for emerging signals.",
    },
}


def label_theme(tag: str) -> str:
    return _THEME_LABELS.get(tag, tag.replace("_", " "))


def format_systems_list(systems: list[str]) -> str:
    if not systems:
        return "no systems"
    if len(systems) == 1:
        return systems[0]
    if len(systems) == 2:
        return f"{systems[0]} and {systems[1]}"
    return ", ".join(systems[:-1]) + f", and {systems[-1]}"


def _clean_themes(themes: list[str]) -> list[str]:
    return [theme for theme in themes if isinstance(theme, str) and not theme.startswith("window:")]


def _primary_themes(themes: list[str], limit: int = 2) -> list[str]:
    cleaned = _clean_themes(themes)
    return cleaned[:limit]


def _citation_from_window(window: dict[str, Any]) -> dict[str, Any]:
    return {
        "windowId": window.get("windowId"),
        "themes": window.get("themes", []),
        "systemsAligned": window.get("systemsAligned", []),
        "evidenceCycleIds": window.get("evidenceCycleIds", []),
    }


def _window_title(window: dict[str, Any], templates: dict[str, Any]) -> str:
    polarity = window.get("polarity", "neutral")
    themes = _primary_themes(window.get("themes", []), 1)
    theme_label = label_theme(themes[0]) if themes else "general growth"
    title_map = templates["window_title"]
    return title_map.get(polarity, title_map["neutral"]).format(theme=theme_label)


def _window_paragraphs(window: dict[str, Any], templates: dict[str, Any]) -> list[str]:
    start = window.get("start")
    end = window.get("end")
    polarity = window.get("polarity")
    intensity = float(window.get("intensity", 0.0))
    confidence = float(window.get("confidence", 0.0))
    systems = window.get("systemsAligned", [])
    theme_labels = [label_theme(tag) for tag in _primary_themes(window.get("themes", []), 2)]

    sentences = [
        templates["frame"].format(
            start=start,
            end=end,
            polarity=polarity,
            intensity=intensity,
            confidence=confidence,
        )
    ]
    if theme_labels:
        if len(theme_labels) == 1:
            focus = theme_labels[0]
        else:
            focus = f"{theme_labels[0]} and {theme_labels[1]}"
        sentences.append(templates["theme_focus"].format(themes=focus))
    if isinstance(systems, list) and len(systems) >= 2:
        sentences.append(
            templates["alignment"].format(
                count=len(systems),
                systems=format_systems_list(systems),
            )
        )
    return sentences[:3]


def _window_takeaways(window: dict[str, Any], templates: dict[str, Any]) -> list[str]:
    polarity = window.get("polarity")
    themes = _primary_themes(window.get("themes", []), 1)
    theme_label = label_theme(themes[0]) if themes else "general growth"

    takeaways = templates["takeaways"].get(polarity, templates["takeaways"]["neutral"])
    return [item.format(theme=theme_label) for item in takeaways]


def make_window_entry(window: dict[str, Any], templates: dict[str, Any]) -> dict[str, Any]:
    return {
        "windowId": window.get("windowId"),
        "start": window.get("start"),
        "end": window.get("end"),
        "title": _window_title(window, templates),
        "paragraphs": _window_paragraphs(window, templates),
        "takeaways": _window_takeaways(window, templates),
        "citations": [_citation_from_window(window)],
    }


def make_overview(forecast: dict[str, Any], templates: dict[str, Any]) -> dict[str, Any]:
    top_windows = forecast.get("topWindows", [])
    headline = "No prominent windows in this range."
    citations = []
    if top_windows:
        top = top_windows[0]
        theme = _primary_themes(top.get("themes", []), 1)
        theme_label = label_theme(theme[0]) if theme else "general growth"
        headline = templates["overview_headline"].format(
            theme=theme_label,
            polarity=top.get("polarity"),
        )
        citations = [_citation_from_window(window) for window in top_windows[:2]]
    bullets = list(forecast.get("summary", []))[:6]
    return {"headline": headline, "bullets": bullets, "citations": citations}


def _domain_from_themes(themes: list[str]) -> str:
    theme_set = set(_clean_themes(themes))
    if theme_set & _CAREER_TAGS:
        return "career"
    if theme_set & _RELATIONSHIP_TAGS:
        return "relationships"
    return "growth"


def _domain_headline(domain: str, has_windows: bool, templates: dict[str, Any]) -> str:
    if not has_windows:
        return templates["domain_headline"]["empty"].format(domain=domain)
    return templates["domain_headline"]["default"].format(domain=domain)


def _domain_bullets(windows: list[dict[str, Any]], templates: dict[str, Any]) -> list[str]:
    if not windows:
        return list(templates["domain_empty"])
    bullets = []
    for window in windows[:2]:
        themes = _primary_themes(window.get("themes", []), 1)
        theme_label = label_theme(themes[0]) if themes else "general growth"
        bullets.append(
            templates["domain_bullet"].format(
                start=window.get("start"),
                end=window.get("end"),
                polarity=window.get("polarity"),
                theme=theme_label,
            )
        )
    if len(bullets) == 1:
        bullets.append(templates["domain_fallback"])
    return bullets[:4]


def make_by_domain(forecast: dict[str, Any], templates: dict[str, Any]) -> dict[str, Any]:
    windows = forecast.get("topWindows", [])
    grouped = {"career": [], "relationships": [], "growth": []}
    for window in windows:
        grouped[_domain_from_themes(window.get("themes", []))].append(window)

    response: dict[str, Any] = {}
    for domain, items in grouped.items():
        top_window_ids = [window.get("windowId") for window in items[:3]]
        response[domain] = {
            "headline": _domain_headline(domain, bool(items), templates),
            "bullets": _domain_bullets(items, templates),
            "topWindows": top_window_ids,
        }
    return response


def build_narrative_response(forecast: dict[str, Any], tone: str = "neutral") -> dict[str, Any]:
    templates = _TEMPLATES.get(tone, _TEMPLATES["neutral"])
    meta = forecast.get("meta", {})
    response = {
        "meta": {
            "version": "phase3.2",
            "granularity": meta.get("granularity", "month"),
            "range": meta.get("range", {}),
        },
        "input": forecast.get("input", {}),
        "overview": make_overview(forecast, templates),
        "windows": [make_window_entry(window, templates) for window in forecast.get("topWindows", [])],
        "byDomain": make_by_domain(forecast, templates),
        "style": {"tone": tone if tone in _TEMPLATES else "neutral", "readingLevel": "plain"},
    }
    if meta.get("as_of"):
        response["meta"]["as_of"] = meta.get("as_of")
    return response
