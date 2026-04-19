"""
scraper/google_maps_scraper.py

Scrapes Google Maps business listings via Apify's compass/crawler-google-places actor.
No mock data — requires a valid APIFY_API_TOKEN to run.
"""

import time
import logging
from typing import Any

import config
from apify_client import ApifyClient

log = logging.getLogger(__name__)

ACTOR_ID = "compass/crawler-google-places"


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _build_client() -> ApifyClient:
    """Instantiate the Apify client, raising early if token is missing."""
    if not config.APIFY_API_TOKEN:
        raise RuntimeError(
            "APIFY_API_TOKEN is not set. "
            "Add it to your .env file before running the scraper."
        )
    return ApifyClient(config.APIFY_API_TOKEN)


def _run_actor_with_retry(
    client: ApifyClient,
    query: str,
    max_results: int,
) -> list[dict]:
    """
    Run compass/crawler-google-places for a single query string.

    Actor input reference:
      https://apify.com/compass/crawler-google-places/input-schema

    Retries up to config.MAX_RETRIES times with linear back-off.
    Returns an empty list (and logs an error) if all retries fail —
    allowing the caller to continue with remaining queries rather than
    aborting the whole run.
    """
    run_input: dict[str, Any] = {
        # ── Search ──────────────────────────────────────────────────────────
        "searchStringsArray":        [query],
        "maxCrawledPlacesPerSearch": max_results,

        # ── Language / locale ────────────────────────────────────────────────
        "language":    "en",
        "countryCode": "in",          # change or expose via config if needed

        # ── What to collect ──────────────────────────────────────────────────
        "includeWebResults": False,   # pure Maps data only
        "exportPlaceUrls":   True,    # include the place URL
        "additionalInfo":    True,    # opening hours, price range, etc.
        "maxImages":         0,       # skip images — not needed for leads
        "maxReviews":        0,       # skip review bodies — count only
    }

    for attempt in range(1, config.MAX_RETRIES + 1):
        try:
            log.info(
                "[GoogleMaps] Query='%s' — attempt %d/%d",
                query, attempt, config.MAX_RETRIES,
            )

            run = client.actor(ACTOR_ID).call(run_input=run_input)
            status = run.get("status")

            if status != "SUCCEEDED":
                raise RuntimeError(f"Actor run ended with status: {status!r}")

            items = list(
                client.dataset(run["defaultDatasetId"]).iterate_items()
            )
            log.info(
                "[GoogleMaps] ✓ %d items retrieved for '%s' (run %s)",
                len(items), query, run["id"],
            )
            return items

        except Exception as exc:
            log.warning(
                "[GoogleMaps] Attempt %d/%d failed for '%s': %s",
                attempt, config.MAX_RETRIES, query, exc,
            )
            if attempt < config.MAX_RETRIES:
                wait = config.RETRY_DELAY_S * attempt
                log.info("[GoogleMaps] Retrying in %ds…", wait)
                time.sleep(wait)

    log.error(
        "[GoogleMaps] All %d retries exhausted for query '%s'. Skipping.",
        config.MAX_RETRIES, query,
    )
    return []


# ─── Public API ───────────────────────────────────────────────────────────────

def scrape_google_maps(
    queries: list[str] | None = None,
    max_results: int | None = None,
) -> list[dict[str, Any]]:
    """
    Scrape Google Maps listings via Apify and return raw item dicts.

    Args:
        queries:     Search strings (defaults to config.GOOGLE_MAPS_QUERIES).
        max_results: Max results per query (defaults to config.GOOGLE_MAPS_MAX_RESULTS).

    Returns:
        List of raw dicts as returned by compass/crawler-google-places.
        Each dict typically contains: title, categoryName, address, city,
        phone, phoneUnformatted, website, totalScore, reviewsCount,
        openingHours, url, plusCode, price, and more.

    Raises:
        RuntimeError: If APIFY_API_TOKEN is missing.
    """
    queries     = queries     or config.GOOGLE_MAPS_QUERIES
    max_results = max_results or config.GOOGLE_MAPS_MAX_RESULTS

    client = _build_client()

    all_results: list[dict] = []

    for idx, query in enumerate(queries, 1):
        log.info(
            "[GoogleMaps] (%d/%d) Scraping: '%s'",
            idx, len(queries), query,
        )
        items = _run_actor_with_retry(client, query, max_results)
        all_results.extend(items)

        # Brief pause between queries to avoid hammering the actor scheduler
        if idx < len(queries):
            time.sleep(2)

    log.info(
        "[GoogleMaps] Finished. Total raw records: %d across %d queries.",
        len(all_results), len(queries),
    )
    return all_results