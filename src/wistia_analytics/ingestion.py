from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from wistia_analytics.io import utc_run_id, write_json
from wistia_analytics.wistia_client import WistiaApiError, WistiaClient


@dataclass(frozen=True)
class IngestionResult:
    run_id: str
    raw_root: Path
    media_files: list[Path]
    visitor_files: list[Path]
    event_files: list[Path]
    visitor_warnings: list[str]


def _as_records(payload: Any) -> list[Any]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("visitors", "events", "data", "results"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
    return []


def ingest_media_and_visitors(
    client: WistiaClient,
    media_ids: list[str],
    output_root: Path,
    visitor_per_page: int = 100,
    max_pages: int = 100,
    run_id: str | None = None,
    visitor_start_page: int = 1,
    event_start_page: int = 1,
    include_media: bool = True,
    include_visitors: bool = True,
    include_events: bool = True,
) -> IngestionResult:
    run_id = run_id or utc_run_id()
    media_files: list[Path] = []
    visitor_files: list[Path] = []
    event_files: list[Path] = []
    visitor_warnings: list[str] = []

    for media_id in media_ids:
        if include_media:
            metadata_payload = client.get_media_metadata(media_id)
            metadata_path = (
                output_root / "wistia" / "media_metadata" / f"run_id={run_id}" / f"{media_id}.json"
            )
            write_json(
                metadata_path,
                {
                    "media_id": media_id,
                    "run_id": run_id,
                    "source": "wistia_media_metadata",
                    "payload": metadata_payload,
                },
            )
            media_files.append(metadata_path)

            media_payload = client.get_media_stats(media_id)
            media_path = (
                output_root / "wistia" / "media_stats" / f"run_id={run_id}" / f"{media_id}.json"
            )
            write_json(
                media_path,
                {
                    "media_id": media_id,
                    "run_id": run_id,
                    "source": "wistia_media_stats",
                    "payload": media_payload,
                },
            )
            media_files.append(media_path)

            try:
                by_date_payload = client.get_media_stats_by_date(media_id)
                by_date_path = (
                    output_root
                    / "wistia"
                    / "media_stats_by_date"
                    / f"run_id={run_id}"
                    / f"{media_id}.json"
                )
                write_json(
                    by_date_path,
                    {
                        "media_id": media_id,
                        "run_id": run_id,
                        "source": "wistia_media_stats_by_date",
                        "payload": by_date_payload,
                    },
                )
                media_files.append(by_date_path)
            except WistiaApiError as exc:
                visitor_warnings.append(f"by_date unavailable for {media_id}: {exc}")

        visitor_end_page = visitor_start_page + max_pages - 1
        if include_visitors:
            for page in range(visitor_start_page, visitor_end_page + 1):
                try:
                    visitor_payload = client.get_media_visitors_page(
                        media_id=media_id,
                        page=page,
                        per_page=visitor_per_page,
                    )
                except WistiaApiError as exc:
                    visitor_warnings.append(f"visitor list unavailable for {media_id}: {exc}")
                    break
                records = _as_records(visitor_payload)
                if not records:
                    break

                visitor_path = (
                    output_root
                    / "wistia"
                    / "visitor_stats"
                    / f"run_id={run_id}"
                    / f"media_id={media_id}"
                    / f"page={page}.json"
                )
                write_json(
                    visitor_path,
                    {
                        "media_id": media_id,
                        "run_id": run_id,
                        "source": "wistia_media_visitors",
                        "page": page,
                        "payload": visitor_payload,
                    },
                )
                visitor_files.append(visitor_path)

                if len(records) < visitor_per_page:
                    break
            else:
                visitor_warnings.append(
                    f"visitor pagination reached page cap for {media_id}: "
                    f"pages {visitor_start_page}-{visitor_end_page}"
                )

        event_end_page = event_start_page + max_pages - 1
        if include_events:
            for page in range(event_start_page, event_end_page + 1):
                try:
                    event_payload = client.get_media_events_page(
                        media_id=media_id,
                        page=page,
                        per_page=visitor_per_page,
                    )
                except WistiaApiError as exc:
                    visitor_warnings.append(f"event list unavailable for {media_id}: {exc}")
                    break
                records = _as_records(event_payload)
                if not records:
                    break

                event_path = (
                    output_root
                    / "wistia"
                    / "event_stats"
                    / f"run_id={run_id}"
                    / f"media_id={media_id}"
                    / f"page={page}.json"
                )
                write_json(
                    event_path,
                    {
                        "media_id": media_id,
                        "run_id": run_id,
                        "source": "wistia_media_events",
                        "page": page,
                        "payload": event_payload,
                    },
                )
                event_files.append(event_path)

                if len(records) < visitor_per_page:
                    break
            else:
                visitor_warnings.append(
                    f"event pagination reached page cap for {media_id}: "
                    f"pages {event_start_page}-{event_end_page}"
                )

    return IngestionResult(
        run_id=run_id,
        raw_root=output_root,
        media_files=media_files,
        visitor_files=visitor_files,
        event_files=event_files,
        visitor_warnings=visitor_warnings,
    )
