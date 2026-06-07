from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from wistia_analytics.transform import create_spark, transform_raw_to_curated


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Transform raw Wistia JSON into curated Parquet.")
    parser.add_argument("--raw-root", type=Path, default=Path("data/raw"))
    parser.add_argument("--curated-root", type=Path, default=Path("data/curated"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    spark = create_spark()
    try:
        transform_raw_to_curated(spark=spark, raw_root=args.raw_root, curated_root=args.curated_root)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
