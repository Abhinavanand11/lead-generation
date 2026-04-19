"""
app/services/linkedin.py

Thin service wrapper around the existing LinkedIn scraper.
"""

import logging
from typing import Any

log = logging.getLogger(__name__)


def fetch_linkedin_leads(
    searches: list[dict] | None = None,
) -> list[dict[str, Any]]:
    """
    Invoke the LinkedIn scraper and return normalised lead dicts.

    Args:
        searches: List of search config dicts
                  (keys: keywords, location, industry, company_size, max_results).
                  Falls back to config.LINKEDIN_SEARCHES when None.

    Returns:
        List of normalised dicts from peakydev/leads-scraper-ppe.
        Returns [] on failure (error is logged, not re-raised).
    """
    try:
        from scraper.linkedin_scraper import scrape_linkedin
        results = scrape_linkedin(searches=searches)
        log.info("[LinkedInService] Retrieved %d normalised records.", len(results))
        return results
    except RuntimeError as exc:
        log.error("[LinkedInService] Configuration error: %s", exc)
        raise
    except Exception as exc:
        log.error("[LinkedInService] Scraper failed unexpectedly: %s", exc, exc_info=True)
        return []