"""
app/services/google_maps.py

Thin service wrapper around the existing Google Maps scraper.
Keeps the scraper's internal logic untouched — this module only
handles dependency wiring and error isolation.
"""

import logging
from typing import Any

log = logging.getLogger(__name__)


def fetch_google_maps_leads(
    queries: list[str] | None = None,
    max_results: int | None = None,
) -> list[dict[str, Any]]:
    """
    Invoke the Google Maps scraper and return raw Apify records.

    Args:
        queries:     Search strings. Falls back to config.GOOGLE_MAPS_QUERIES.
        max_results: Per-query cap. Falls back to config.GOOGLE_MAPS_MAX_RESULTS.

    Returns:
        List of raw dicts from compass/crawler-google-places.
        Returns [] on failure (error is logged, not re-raised).
    """
    try:
        # Import here to keep the service independent of import-time side-effects
        from scraper.google_maps_scraper import scrape_google_maps
        results = scrape_google_maps(queries=queries, max_results=max_results)
        log.info("[GMapsService] Retrieved %d raw records.", len(results))
        return results
    except RuntimeError as exc:
        # Missing APIFY_API_TOKEN — surface clearly
        log.error("[GMapsService] Configuration error: %s", exc)
        raise
    except Exception as exc:
        log.error("[GMapsService] Scraper failed unexpectedly: %s", exc, exc_info=True)
        return []