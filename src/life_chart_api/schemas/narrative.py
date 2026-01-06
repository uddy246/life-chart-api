from __future__ import annotations

from typing import List, Literal

from pydantic import Field, model_validator

from life_chart_api.schemas.core_types import SourceField, StrictBaseModel

NarrativeSectionId = Literal[
    "internal_experience",
    "external_demands",
    "tension",
    "why_tension_exists",
    "phase",
]

REQUIRED_SECTION_ORDER: List[NarrativeSectionId] = [
    "internal_experience",
    "external_demands",
    "tension",
    "why_tension_exists",
    "phase",
]


class NarrativeSection(StrictBaseModel):
    id: NarrativeSectionId
    title: str
    body: str
    source_fields: List[SourceField]
    preamble: str | None = None
    safeguard: str | None = None

    @model_validator(mode="after")
    def _validate_optional_fields(self) -> "NarrativeSection":
        if self.id != "external_demands" and self.preamble is not None:
            raise ValueError("preamble is only allowed for external_demands")
        if self.id != "phase" and self.safeguard is not None:
            raise ValueError("safeguard is only allowed for phase")
        if self.id == "external_demands" and self.preamble is None:
            raise ValueError("external_demands requires preamble")
        if self.id == "phase" and self.safeguard is None:
            raise ValueError("phase requires safeguard")
        return self


class Narrative(StrictBaseModel):
    version: str
    sections: List[NarrativeSection]

    @model_validator(mode="after")
    def _validate_order(self) -> "Narrative":
        ids = [section.id for section in self.sections]
        if ids != REQUIRED_SECTION_ORDER:
            raise ValueError("narrative sections must match required order")
        return self
