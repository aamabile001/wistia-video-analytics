from __future__ import annotations

import pytest

from pathlib import Path

from wistia_analytics.config import get_wistia_token, load_project_env


def test_get_wistia_token_requires_environment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("WISTIA_API_TOKEN", raising=False)

    with pytest.raises(RuntimeError):
        get_wistia_token()


def test_get_wistia_token_reads_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WISTIA_API_TOKEN", "secret-token")

    assert get_wistia_token() == "secret-token"


def test_load_project_env_reads_nearest_dotenv(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text("WISTIA_API_TOKEN=dotenv-token\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("WISTIA_API_TOKEN", raising=False)

    assert load_project_env() == env_path
    assert get_wistia_token() == "dotenv-token"
