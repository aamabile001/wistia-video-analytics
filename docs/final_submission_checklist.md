# Final Submission Checklist

## Requirements Coverage

- [x] AWS architecture for ingestion, storage, processing, and reporting.
- [x] Token-based Wistia API authentication through local `.env`.
- [x] Media metadata ingestion.
- [x] Media stats ingestion.
- [x] Visitor-level ingestion.
- [x] Event-level ingestion.
- [x] Pagination and resumable pagination.
- [x] PySpark transformation.
- [x] Dimensional model: `dim_media`, `dim_visitor`, `fact_media_engagement`.
- [x] S3 raw and curated storage.
- [x] Glue Data Catalog tables.
- [x] GitHub repo with CI validation.
- [x] Streamlit dashboard.
- [ ] Seven successful production-mode runs recorded in `docs/run_evidence.md`.
- [ ] Final dashboard screenshots or demo ready.
- [ ] Athena validation queries run from `docs/athena_validation_queries.sql`.
- [ ] Screenshots captured using `docs/screenshot_checklist.md`.
- [ ] Known limitations reviewed in `docs/known_limitations.md`.
- [ ] Recorded walkthrough completed.

## Known Limitations

- Wistia returns large visitor/event histories. Exhaustive historical backfill may require multiple resumable chunks.
- The current ingestion strategy is run-based and page-resumable. Timestamp-filtered incremental pulls should be added if Wistia confirms reliable filtering parameters for these endpoints.
- `v08dlrgr7v` had more visitor/event pages than the bounded production-scale pull captured on 2026-06-08.

## Final Reviewer Path

1. Read `README.md`.
2. Review `docs/architecture.md`.
3. Review `docs/data_model.md`.
4. Review `docs/runbook.md`.
5. Review `docs/run_evidence.md`.
6. Review `docs/athena_validation_queries.sql`.
7. Review `docs/known_limitations.md`.
8. Inspect source code under `src/wistia_analytics`.
9. Run tests with `python -m pytest`.
