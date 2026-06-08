# Production Run Evidence

Use this log to prove the pipeline ran in production mode for seven successful runs.

## Run Checklist

For each run:

1. Run Wistia ingestion.
2. Resume pagination chunks if a media endpoint still returns full 100-record pages.
3. Run the PySpark transformation.
4. Sync raw and curated outputs to S3.
5. Refresh Glue partitions.
6. Record row counts and notes below.

## Evidence Log

| Run # | Date | Run ID | Media IDs | Ingestion Scope | dim_media Rows | dim_visitor Rows | fact_media_engagement Rows | S3 Raw Synced | S3 Curated Synced | Glue Partitions | Notes |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- | --- | ---: | --- |
| 1 | 2026-06-08 | 20260608T135031Z | gskhw4w4lm, v08dlrgr7v | Bounded large pull; v08dlrgr7v visitors/events capped and resumable | 2 | 106,733 | 220,470 | Yes | Yes | 776 | gskhw4w4lm events completed at page 165 with 62 records. v08dlrgr7v visitors reached page 1000 with 100 records; v08dlrgr7v events reached page 375 with 100 records. Continue with resumable commands if exhaustive backfill is required. |
| 2 |  |  |  |  |  |  |  |  |  |  |  |
| 3 |  |  |  |  |  |  |  |  |  |  |  |
| 4 |  |  |  |  |  |  |  |  |  |  |  |
| 5 |  |  |  |  |  |  |  |  |  |  |  |
| 6 |  |  |  |  |  |  |  |  |  |  |  |
| 7 |  |  |  |  |  |  |  |  |  |  |  |

## Daily Commands

```powershell
python scripts/run_ingestion.py --media-ids gskhw4w4lm v08dlrgr7v --output-root data/raw --visitor-per-page 100 --max-pages 500
python scripts/run_local_pyspark_pipeline.py --raw-root data/raw --curated-root data/curated_spark
```

Sync raw and curated data:

```powershell
$env:AWS_SHARED_CREDENTIALS_FILE = "..\.aws\credentials"
$env:AWS_CONFIG_FILE = "..\.aws\config"
aws s3 sync data/raw s3://wistia-video-analytics-768205044248-us-east-1/raw/ --exclude "*.crc" --profile wistia-project --region us-east-1
aws s3 sync data/curated_spark s3://wistia-video-analytics-768205044248-us-east-1/curated/ --delete --exclude "*.crc" --profile wistia-project --region us-east-1
aws s3 rm s3://wistia-video-analytics-768205044248-us-east-1/curated/ --recursive --exclude "*" --include "*.crc" --profile wistia-project --region us-east-1
```

Record row counts:

```powershell
python -c "import pandas as pd; from pathlib import Path; root=Path('data/curated_spark'); [print(f'{name}: {len(pd.read_parquet(root/name)):,}') for name in ['dim_media','dim_visitor','fact_media_engagement']]"
```
