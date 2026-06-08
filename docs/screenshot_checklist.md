# Screenshot Checklist

Capture these screenshots for the final walkthrough package.

## Local Evidence

- `pytest` passing in the project terminal.
- Streamlit dashboard home view.
- Streamlit media performance table.
- Streamlit visitor geography section showing known vs Unknown visitor geography counts and the explanatory caption about Wistia source coverage.
- Streamlit visitor sample showing masked visitor IDs and masked IP addresses.
- `docs/run_evidence.md` showing completed runs.

## AWS Evidence

- S3 bucket `wistia-video-analytics-768205044248-us-east-1` showing the `raw/` prefix.
- S3 bucket showing the `curated/` prefix.
- Glue database `wistia_video_analytics`.
- Glue table list showing `dim_media`, `dim_visitor`, and `fact_media_engagement`.
- Athena query editor with row count validation from `docs/athena_validation_queries.sql`.

## GitHub Evidence

- Repository homepage.
- Latest commit history showing project closeout commits.
- GitHub Actions test workflow passing, if available.

## Suggested File Naming

```text
screenshots/
  01-pytest-passing.png
  02-streamlit-dashboard.png
  03-s3-raw-prefix.png
  04-s3-curated-prefix.png
  05-glue-tables.png
  06-athena-validation.png
  07-github-actions.png
```
