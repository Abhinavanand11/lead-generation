"""
main.py

B2B Lead Generation Pipeline — entry point.

Execution order:
  1. Scrape Google Maps  (Apify actor or mock data)
  2. Scrape LinkedIn     (mock / placeholder)
  3. Parse raw records   → unified lead schema
  4. Validate leads      (name + phone/email required)
  5. Deduplicate         (by phone+name or company+name)
  6. Export to Excel     (3 data sheets + summary)
"""

import logging
import sys
import os

import config

# ─── Logging bootstrap (must happen before any other import) ──────────────────

log = logging.getLogger(__name__)


# ─── Pipeline ─────────────────────────────────────────────────────────────────

def run_pipeline() -> str:
    """
    Execute the full B2B lead generation pipeline.

    Returns:
        Absolute path of the generated Excel file.
    """
    log.info("=" * 65)
    log.info("  B2B Lead Generation Pipeline — starting")
    log.info("=" * 65)

    # ── Step 1: Scrape Google Maps ─────────────────────────────────────────
    log.info("")
    log.info("── STEP 1/5 · Google Maps Scraping ────────────────────────────")
    try:
        from scraper.google_maps_scraper import scrape_google_maps
        gm_raw = scrape_google_maps()
        log.info("  ✓ Google Maps raw records: %d", len(gm_raw))
    except Exception as exc:
        log.error("  Google Maps scraping failed: %s", exc, exc_info=True)
        gm_raw = []

    # ── Step 2: Scrape LinkedIn ────────────────────────────────────────────
    log.info("")
    log.info("── STEP 2/5 · LinkedIn Scraping ────────────────────────────────")
    try:
        from scraper.linkedin_scraper import scrape_linkedin
        li_raw = scrape_linkedin()
        log.info("  ✓ LinkedIn raw records: %d", len(li_raw))
    except Exception as exc:
        log.error("  LinkedIn scraping failed: %s", exc, exc_info=True)
        li_raw = []

    if not gm_raw and not li_raw:
        log.error("  No data collected from either source. Aborting.")
        sys.exit(1)

    # ── Step 3: Parse ──────────────────────────────────────────────────────
    log.info("")
    log.info("── STEP 3/5 · Parsing & Normalisation ─────────────────────────")
    try:
        from processing.parser import parse_all
        leads = parse_all(gm_raw, li_raw)
        log.info("  ✓ Parsed leads: %d", len(leads))
    except Exception as exc:
        log.error("  Parsing failed: %s", exc, exc_info=True)
        sys.exit(1)

    # ── Step 4: Validate ───────────────────────────────────────────────────
    log.info("")
    log.info("── STEP 4/5 · Validation ───────────────────────────────────────")
    try:
        from processing.validator import validate_leads
        valid_leads, rejected = validate_leads(leads)
        log.info("  ✓ Valid: %d  |  Rejected: %d", len(valid_leads), len(rejected))
        if rejected:
            log.info("  Rejection reasons preview (first 3):")
            for r in rejected[:3]:
                log.info("    • name='%s' phone='%s' email='%s'",
                         r.get("name"), r.get("phone"), r.get("email"))
    except Exception as exc:
        log.error("  Validation failed: %s", exc, exc_info=True)
        sys.exit(1)

    # ── Step 5: Deduplicate ────────────────────────────────────────────────
    log.info("")
    log.info("── STEP 5/5 · Deduplication ────────────────────────────────────")
    try:
        from processing.deduplicator import deduplicate
        unique_leads, removed_count = deduplicate(valid_leads)
        log.info("  ✓ Unique leads: %d  |  Duplicates removed: %d",
                 len(unique_leads), removed_count)
    except Exception as exc:
        log.error("  Deduplication failed: %s", exc, exc_info=True)
        sys.exit(1)

    # ── Step 6: Export ─────────────────────────────────────────────────────
    log.info("")
    log.info("── STEP 6/6 · Excel Export ─────────────────────────────────────")
    try:
        from exporter.excel_exporter import export_to_excel
        output_path = export_to_excel(unique_leads)
        log.info("  ✓ Excel file saved: %s", output_path)
    except Exception as exc:
        log.error("  Export failed: %s", exc, exc_info=True)
        sys.exit(1)

    # ── Final summary ──────────────────────────────────────────────────────
    log.info("")
    log.info("=" * 65)
    log.info("  ✅ Pipeline complete!")
    log.info("  📊 Total leads exported : %d", len(unique_leads))
    log.info("  📁 Output file          : %s", output_path)
    log.info("=" * 65)

    return output_path


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_pipeline()
