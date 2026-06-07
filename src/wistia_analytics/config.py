from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


DEFAULT_MEDIA_IDS = ("gskhw4w4lm", "v08dlrgr7v")


@dataclass(frozen=True)
class PipelineConfig:
    media_ids: tuple[str, ...] = DEFAULT_MEDIA_IDS
    raw_root: Path = Path("data/raw")
    curated_root: Path = Path("data/curated")
    api_base_url: str = "https://api.wistia.com/v1"


def load_project_env(start: Path | None = None) -> Path | None:
    """Load the nearest local .env without printing or persisting secrets."""
    current = (start or Path.cwd()).resolve()
    search_roots = [current, *current.parents]
    for root in search_roots:
        env_path = root / ".env"
        if env_path.exists():
            load_dotenv(env_path, override=False)
            return env_path
    return None


def get_wistia_token() -> str:
    load_project_env()
    token = os.getenv("WISTIA_API_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "WISTIA_API_TOKEN is not set. Add it to the local .env file; do not hardcode it."
        )
    return token
