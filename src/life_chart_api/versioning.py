API_VERSION = "v1"

SCHEMA_VERSION_PROFILE = "1.0.0"
SCHEMA_VERSION_TIMELINE = "phase2.3"
SCHEMA_VERSION_TIMELINE_SCAFFOLD = "phase2.1"
SCHEMA_VERSION_FORECAST = "phase2.4"
SCHEMA_VERSION_NARRATIVE = "phase3.2"
SCHEMA_VERSION_ERROR = "v1"


def schema_version_for_path(path: str) -> str:
    if path.startswith("/profile/compute"):
        return SCHEMA_VERSION_PROFILE
    if path.startswith("/profile/timeline/scaffold"):
        return SCHEMA_VERSION_TIMELINE_SCAFFOLD
    if path.startswith("/profile/timeline"):
        return SCHEMA_VERSION_TIMELINE
    if path.startswith("/profile/forecast"):
        return SCHEMA_VERSION_FORECAST
    if path.startswith("/profile/narrative"):
        return SCHEMA_VERSION_NARRATIVE
    if path.startswith("/numerology/compute"):
        return "v1"
    if path.startswith("/meta"):
        return "v1"
    return "unknown"
