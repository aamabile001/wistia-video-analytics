from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from wistia_analytics.config import DEFAULT_MEDIA_IDS, get_wistia_token
from wistia_analytics.ingestion import ingest_media_and_visitors
from wistia_analytics.wistia_client import WistiaClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest Wistia media and visitor stats.")
    parser.add_argument("--media-ids", nargs="+", default=list(DEFAULT_MEDIA_IDS))
    parser.add_argument("--output-root", type=Path, default=Path("data/raw"))
    parser.add_argument("--visitor-per-page", type=int, default=100)
    parser.add_argument("--max-pages", type=int, default=100)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = WistiaClient(token=get_wistia_token())
    result = ingest_media_and_visitors(
        client=client,
        media_ids=args.media_ids,
        output_root=args.output_root,
        visitor_per_page=args.visitor_per_page,
        max_pages=args.max_pages,
    )
    print(f"run_id={result.run_id}")
    print(f"media_files={len(result.media_files)}")
    print(f"visitor_files={len(result.visitor_files)}")
    print(f"event_files={len(result.event_files)}")
    for warning in result.visitor_warnings:
        print(f"warning={warning}")


if __name__ == "__main__":
    main()
