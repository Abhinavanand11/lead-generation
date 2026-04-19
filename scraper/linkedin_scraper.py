"""
scraper/linkedin_scraper.py

LinkedIn lead collection via Apify's peakydev/leads-scraper-ppe actor.
No mock data — requires a valid APIFY_API_TOKEN to run.

Actor reference:
  https://apify.com/peakydev/leads-scraper-ppe
"""

import time
import logging
from typing import Any

import config
from apify_client import ApifyClient

log = logging.getLogger(__name__)

ACTOR_ID = "peakydev/leads-scraper-ppe"


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _build_client() -> ApifyClient:
    """Instantiate the Apify client, raising early if token is missing."""
    if not config.APIFY_API_TOKEN:
        raise RuntimeError(
            "APIFY_API_TOKEN is not set. "
            "Add it to your .env file before running the scraper."
        )
    return ApifyClient(config.APIFY_API_TOKEN)


def _build_run_input(search_config: dict) -> dict[str, Any]:
    """
    Build the actor input payload from a search config dict.

    search_config keys (all optional — actor uses its own defaults otherwise):
      keywords      (str)  — job title / role keywords, e.g. "CTO"
      location      (str)  — city or country, e.g. "Mumbai"
      industry      (str)  — LinkedIn industry filter
      company_size  (str)  — e.g. "11-50", "51-200"
      max_results   (int)  — maximum profiles to collect

    Actor input schema reference:
      https://apify.com/peakydev/leads-scraper-ppe/input-schema
    """
    run_input: dict[str, Any] = {}

    if search_config.get("keywords"):
        run_input["searchKeywords"] = search_config["keywords"]

    if search_config.get("location"):
        run_input["location"] = search_config["location"]

    if search_config.get("industry"):
        run_input["industry"] = search_config["industry"]

    if search_config.get("company_size"):
        run_input["companySize"] = search_config["company_size"]

    max_results = search_config.get("max_results") or config.LINKEDIN_MAX_RESULTS
    run_input["maxResults"] = max_results

    return run_input


def _run_actor_with_retry(
    client: ApifyClient,
    search_config: dict,
) -> list[dict]:
    """
    Run peakydev/leads-scraper-ppe for a single search config.

    Retries up to config.MAX_RETRIES times with linear back-off.
    Returns an empty list (and logs an error) if all retries fail.
    """
    run_input = _build_run_input(search_config)
    label = search_config.get("keywords", "unnamed")

    for attempt in range(1, config.MAX_RETRIES + 1):
        try:
            log.info(
                "[LinkedIn] Search='%s' — attempt %d/%d | input=%s",
                label, attempt, config.MAX_RETRIES, run_input,
            )

            run = client.actor(ACTOR_ID).call(run_input=run_input)
            status = run.get("status")

            if status != "SUCCEEDED":
                raise RuntimeError(f"Actor run ended with status: {status!r}")

            items = list(
                client.dataset(run["defaultDatasetId"]).iterate_items()
            )
            log.info(
                "[LinkedIn] ✓ %d profiles retrieved for '%s' (run %s)",
                len(items), label, run["id"],
            )
            return items

        except Exception as exc:
            log.warning(
                "[LinkedIn] Attempt %d/%d failed for '%s': %s",
                attempt, config.MAX_RETRIES, label, exc,
            )
            if attempt < config.MAX_RETRIES:
                wait = config.RETRY_DELAY_S * attempt
                log.info("[LinkedIn] Retrying in %ds…", wait)
                time.sleep(wait)

    log.error(
        "[LinkedIn] All %d retries exhausted for search '%s'. Skipping.",
        config.MAX_RETRIES, label,
    )
    return []


def _normalise_item(raw: dict) -> dict[str, Any]:
    """
    Normalise a single raw peakydev/leads-scraper-ppe item into a
    consistent flat dict that matches the rest of the pipeline's schema.

    The actor may return different field names across versions; this function
    handles common aliases so downstream code never has to worry about them.
    """
    # Name — try fullName, then compose from first/last
    name = (
        raw.get("fullName")
        or raw.get("name")
        or " ".join(filter(None, [raw.get("firstName"), raw.get("lastName")]))
    ).strip()

    # Company — varies across actor versions
    company = (
        raw.get("company")
        or raw.get("companyName")
        or raw.get("currentCompany")
        or ""
    ).strip()

    # Job title
    job_title = (
        raw.get("jobTitle")
        or raw.get("title")
        or raw.get("headline")
        or ""
    ).strip()

    # Contact
    email = (raw.get("email") or "").strip()
    phone = (
        raw.get("phone")
        or raw.get("phoneNumber")
        or ""
    ).strip()

    # Location
    city = (
        raw.get("city")
        or raw.get("location")
        or raw.get("locationName")
        or ""
    ).strip()

    return {
        "name":         name,
        "company":      company,
        "job_title":    job_title,
        "linkedin_url": raw.get("linkedinUrl") or raw.get("profileUrl") or "",
        "email":        email,
        "phone":        phone,
        "city":         city,
        # Pass through the full raw dict for debugging / future enrichment
        "_raw":         raw,
    }


# ─── Public API ───────────────────────────────────────────────────────────────

def scrape_linkedin(
    searches: list[dict] | None = None,
) -> list[dict[str, Any]]:
    """
    Scrape LinkedIn profiles/leads via Apify and return normalised dicts.

    Args:
        searches: List of search config dicts. Each dict may contain:
                    keywords, location, industry, company_size, max_results.
                  Defaults to config.LINKEDIN_SEARCHES if not provided.

    Returns:
        List of normalised lead dicts with keys:
          name, company, job_title, linkedin_url, email, phone, city, _raw.

    Raises:
        RuntimeError: If APIFY_API_TOKEN is missing.

    Example:
        leads = scrape_linkedin([
            {"keywords": "CTO", "location": "Mumbai", "max_results": 25},
            {"keywords": "Founder", "location": "Bangalore", "max_results": 25},
        ])
    """
    searches = searches or config.LINKEDIN_SEARCHES

    if not searches:
        log.warning(
            "[LinkedIn] No search configs provided and LINKEDIN_SEARCHES is empty. "
            "Nothing to scrape."
        )
        return []

    client = _build_client()
    all_results: list[dict] = []

    for idx, search_config in enumerate(searches, 1):
        log.info(
            "[LinkedIn] (%d/%d) Running search: %s",
            idx, len(searches), search_config,
        )
        raw_items = _run_actor_with_retry(client, search_config)
        normalised = [_normalise_item(item) for item in raw_items]

        # Drop entries with neither a name nor a company — not useful as leads
        valid = [l for l in normalised if l["name"] or l["company"]]
        dropped = len(normalised) - len(valid)
        if dropped:
            log.debug("[LinkedIn] Dropped %d items with no name/company.", dropped)

        all_results.extend(valid)

        if idx < len(searches):
            time.sleep(2)

    log.info(
        "[LinkedIn] Finished. Total normalised records: %d across %d searches.",
        len(all_results), len(searches),
    )
    return all_results