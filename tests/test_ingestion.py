from __future__ import annotations

from pathlib import Path
from typing import Any

from wistia_analytics.ingestion import ingest_media_and_visitors


class FakeClient:
    def get_media_metadata(self, media_id: str) -> dict[str, Any]:
        return {"hashed_id": media_id, "name": "Test Video"}

    def get_media_stats(self, media_id: str) -> dict[str, Any]:
        return {"media_id": media_id, "title": "Test Video"}

    def get_media_stats_by_date(self, media_id: str) -> list[dict[str, Any]]:
        return [{"media_id": media_id, "date": "2026-06-07", "play_count": 1}]

    def get_media_visitors_page(self, media_id: str, page: int, per_page: int) -> dict[str, Any]:
        if page > 1:
            return {"visitors": []}
        return {"visitors": [{"visitor_key": "visitor-1", "media_id": media_id}]}

    def get_media_events_page(self, media_id: str, page: int, per_page: int) -> dict[str, Any]:
        if page > 1:
            return {"events": []}
        return {"events": [{"event_key": "event-1", "visitor_key": "visitor-1", "media_id": media_id}]}


def test_ingestion_writes_raw_files(tmp_path: Path) -> None:
    result = ingest_media_and_visitors(
        client=FakeClient(),  # type: ignore[arg-type]
        media_ids=["abc123"],
        output_root=tmp_path,
    )

    assert result.run_id
    assert len(result.media_files) == 3
    assert len(result.visitor_files) == 1
    assert len(result.event_files) == 1
    assert result.media_files[0].exists()
    assert result.visitor_files[0].exists()
