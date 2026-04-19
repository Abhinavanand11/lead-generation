"""
app/services/pipeline.py

Orchestrates the full B2B lead generation pipeline:
  1. Scrape Google Maps
  2. Scrape LinkedIn
  3. Parse raw records  → unified schema
  4. Validate leads
  5. Deduplicate
  6. Export to Excel

This module is intentionally synchronous — it wraps blocking I/O
(Apify HTTP calls, openpyxl file writes). FastAPI routes execute it
inside a threadpool via `asyncio.to_thread` so the event loop stays free.
"""

import logging
from typing import Any

from app.services.google_maps import fetch_google_maps_leads
from app.services.linkedin   import fetch_linkedin_leads
from app.schemas.lead        import PipelineStats

log = logging.getLogger(__name__)


def run_pipeline(
    queries:            list[str] | None = None,
    linkedin_searches:  list[dict] | None = None,
    include_leads:      bool = False,
) -> dict[str, Any]:
    """
    Execute the full pipeline synchronously.

    Args:
        queries:           Google Maps search strings.
        linkedin_searches: LinkedIn search configs.
        include_leads:     Whether to return a leads preview in the result.

    Returns:
        {
            "total_leads": int,
            "output_file": str,
            "stats":       PipelineStats,
            "leads":       list[dict] | None,  # first 20 if include_leads=True
        }

    Raises:
        RuntimeError: If APIFY_API_TOKEN is missing.
        Exception:    On unrecoverable pipeline failure.
    """
    log.info("=" * 60)
    log.info("  Pipeline run starting")
    log.info("=" * 60)

    # ── Step 1: Scrape ────────────────────────────────────────────────────
    log.info("[Pipeline] Step 1/5 — Google Maps scraping")
    gm_raw = fetch_google_maps_leads(queries=queries)

    log.info("[Pipeline] Step 2/5 — LinkedIn scraping")
    li_raw = fetch_linkedin_leads(searches=linkedin_searches)

    if not gm_raw and not li_raw:
        raise RuntimeError(
            "Both scrapers returned no data. "
            "Check your APIFY_API_TOKEN and search configuration."
        )

    # ── Step 2: Parse ─────────────────────────────────────────────────────
    log.info("[Pipeline] Step 3/5 — Parsing & normalisation")
    from processing.parser import parse_all
    leads = parse_all(gm_raw, li_raw)

    # ── Step 3: Validate ──────────────────────────────────────────────────
    log.info("[Pipeline] Step 4/5 — Validation")
    from processing.validator import validate_leads
    valid_leads, rejected = validate_leads(leads)

    # ── Step 4: Deduplicate ───────────────────────────────────────────────
    log.info("[Pipeline] Step 5/5 — Deduplication")
    from processing.deduplicator import deduplicate
    unique_leads, removed_count = deduplicate(valid_leads)

    # ── Step 5: Export ────────────────────────────────────────────────────
    log.info("[Pipeline] Step 6/6 — Excel export")
    from exporter.excel_exporter import export_to_excel
    output_path = export_to_excel(unique_leads)

    stats = PipelineStats(
        google_maps_raw=len(gm_raw),
        linkedin_raw=len(li_raw),
        parsed=len(leads),
        valid=len(valid_leads),
        rejected=len(rejected),
        duplicates_removed=removed_count,
        unique=len(unique_leads),
    )

    log.info("=" * 60)
    log.info("  ✅ Pipeline complete — %d unique leads → %s", len(unique_leads), output_path)
    log.info("=" * 60)

    result: dict[str, Any] = {
        "total_leads": len(unique_leads),
        "output_file": output_path,
        "stats":       stats,
        "leads":       None,
    }

    if include_leads:
        result["leads"] = unique_leads[:20]

    return result