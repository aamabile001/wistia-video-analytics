from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import requests


class WistiaApiError(RuntimeError):
    """Raised when Wistia returns a non-retryable or exhausted API error."""


@dataclass
class WistiaClient:
    token: str
    base_url: str = "https://api.wistia.com/v1"
    timeout_seconds: int = 30
    max_retries: int = 3
    backoff_seconds: float = 1.5

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "X-Wistia-API-Version": "2026-03",
        }

    def get_json(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = path if path.startswith("https://") else f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.get(
                    url,
                    headers=self._headers(),
                    params=params,
                    timeout=self.timeout_seconds,
                )
                if response.status_code in {429, 500, 502, 503, 504}:
                    raise WistiaApiError(
                        f"Retryable Wistia error {response.status_code}: {response.text[:300]}"
                    )
                if response.status_code == 401:
                    raise WistiaApiError("Unauthorized Wistia request. Check token permissions.")
                if response.status_code == 404:
                    raise WistiaApiError(f"Wistia resource not found: {url}")
                response.raise_for_status()
                return response.json()
            except (requests.RequestException, WistiaApiError) as exc:
                last_error = exc
                if attempt == self.max_retries:
                    break
                time.sleep(self.backoff_seconds * attempt)

        raise WistiaApiError(f"Wistia request failed after retries: {last_error}") from last_error

    def get_media_stats(self, media_id: str) -> dict[str, Any]:
        return self.get_json(f"stats/medias/{media_id}.json")

    def get_media_metadata(self, media_id: str) -> dict[str, Any]:
        return self.get_json(f"medias/{media_id}.json")

    def get_media_stats_by_date(self, media_id: str) -> Any:
        return self.get_json(f"https://api.wistia.com/modern/stats/medias/{media_id}/by_date")

    def get_media_visitors_page(self, media_id: str, page: int = 1, per_page: int = 100) -> Any:
        return self.get_json(
            f"stats/medias/{media_id}/visitors.json",
            params={"page": page, "per_page": per_page},
        )
