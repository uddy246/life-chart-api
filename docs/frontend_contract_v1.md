# Frontend Contract v1 (Lovable)

Purpose
The Lovable frontend consumes `/profile/narrative` as the primary, stable contract.
This document defines the v1 contract and stability guarantees.

Primary endpoint
- `/profile/narrative`: primary frontend contract (deterministic, schema-driven narrative).

Secondary endpoints
- `/profile/forecast`: optional UI layers (ranked windows and summaries).
- `/profile/timeline`: debug/advanced view of cycles and intersections.
- `/profile/compute`: internal/advanced use; not required by Lovable.
- `/meta`, `/health`, `/ready`, `/metrics`: ops and diagnostics.

/profile/narrative request params
- `include`: CSV of systems. Allowed: `western,vedic,chinese`. Default: `western,vedic,chinese`.
- `from`: `YYYY-MM`. Default: `2026-01`.
- `to`: `YYYY-MM`. Default: `2027-12`.
- `granularity`: `month|quarter`. Default: `month`.
- `tone`: `neutral|direct|reflective`. Default: `neutral`.
- `as_of`: `YYYY-MM-DD` (optional). Default: omitted.

Response shape (high-level)
- `overview`: headline + bullets + citations.
- `windows`: ordered list; each entry includes title, short paragraphs, takeaways, and citations.
- `byDomain`: grouped summaries (career/relationships/growth).
- `citations` rule: every overview and window entry includes citations with:
  `windowId`, `themes`, `systemsAligned`, `evidenceCycleIds`.

Headers
- `X-API-Version`: API version string (v1).
- `X-Schema-Version`: endpoint schema version (e.g., phase3.2 for narrative).
- `X-Request-Id`: request correlation id.

Error envelope contract
```
{
  "error": {
    "code": "INVALID_INPUT|VALIDATION_FAILED|RATE_LIMITED|INTERNAL_ERROR|NOT_FOUND",
    "message": "Human-readable summary",
    "details": [{ "path": "query.from", "issue": "must match YYYY-MM" }],
    "requestId": "optional"
  }
}
```

Stability guarantee (Core v1)
- Additive-only changes for v1.
- Breaking changes require v2 (new endpoints or schema versions).
- Any contract change must update schemas, examples, and the golden snapshot test.

Versioning policy
- v1.0.x: patch-level, no behavior changes.
- v1.x: additive, backward-compatible changes.
- v2: breaking changes, new contract.

Example curl (no external URLs)
```
curl -s "http://localhost:8000/profile/narrative?include=western,vedic,chinese&from=2026-01&to=2027-12&granularity=month&tone=neutral"
```

References
- Narrative schema: `src/life_chart_api/schemas/narrative/narrative_response.schema.json`
- Narrative example: `src/life_chart_api/schemas/examples/narrative/narrative_response.example.json`
