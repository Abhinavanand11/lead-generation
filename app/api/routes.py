"""
app/api/routes.py

All API endpoints for the B2B Lead Generation service.

Endpoints:
  GET  /health         — liveness check
  POST /scrape         — run full pipeline
  GET  /download       — download latest Excel export
"""

import asyncio
import logging
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

import app.config as cfg
from app.schemas.lead   import ScrapeRequest, ScrapeResponse, HealthResponse, Lead
from app.services.pipeline import run_pipeline

log = logging.getLogger(__name__)

router = APIRouter()


# ─── Health ───────────────────────────────────────────────────────────────────

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness check",
    tags=["Health"],
)
async def health() -> HealthResponse:
    """Returns API status and whether the Apify token is configured."""
    return HealthResponse(
        status="ok",
        apify_token_set=bool(cfg.APIFY_API_TOKEN),
    )


# ─── Scrape ───────────────────────────────────────────────────────────────────

@router.post(
    "/scrape",
    response_model=ScrapeResponse,
    summary="Run the full lead generation pipeline",
    tags=["Pipeline"],
    responses={
        200: {"description": "Pipeline completed successfully"},
        422: {"description": "Validation error in request body"},
        500: {"description": "Pipeline failure (scraper error, missing token, etc.)"},
    },
)
async def scrape(body: ScrapeRequest) -> ScrapeResponse:
    """
    Trigger the full B2B lead generation pipeline:

    1. Scrape Google Maps via Apify
    2. Scrape LinkedIn via Apify
    3. Parse → validate → deduplicate
    4. Export to Excel

    The pipeline runs in a background thread so the async event loop
    stays responsive. Large scrape jobs may take several minutes.
    """
    log.info(
        "[/scrape] Request received — %d GM queries, %d LI searches, preview=%s",
        len(body.queries), len(body.linkedin_searches), body.include_leads_preview,
    )

    try:
        result = await asyncio.to_thread(
            run_pipeline,
            queries=body.queries or None,
            linkedin_searches=body.linkedin_searches or None,
            include_leads=body.include_leads_preview,
        )
    except RuntimeError as exc:
        # E.g. missing APIFY_API_TOKEN or both scrapers returned nothing
        log.error("[/scrape] Pipeline RuntimeError: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        log.error("[/scrape] Unexpected pipeline failure: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {exc}")

    leads_preview = None
    if result.get("leads"):
        leads_preview = [Lead(**lead) for lead in result["leads"]]

    log.info("[/scrape] Done — %d leads, file: %s", result["total_leads"], result["output_file"])

    return ScrapeResponse(
        status="success",
        total_leads=result["total_leads"],
        output_file=result["output_file"],
        stats=result["stats"],
        leads=leads_preview,
    )


# ─── Download ─────────────────────────────────────────────────────────────────

@router.get(
    "/download",
    summary="Download the latest Excel export",
    tags=["Export"],
    responses={
        200: {"description": "Excel file download"},
        404: {"description": "No export file found — run /scrape first"},
    },
)
async def download_latest():
    """
    Return the most recently generated Excel file as a download.

    The file is resolved from the configured OUTPUT_DIR / OUTPUT_FILENAME.
    Run POST /scrape first to generate the file.
    """
    output_path = Path(cfg.OUTPUT_DIR) / cfg.OUTPUT_FILENAME

    if not output_path.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                f"No export file found at '{output_path}'. "
                "Run POST /scrape to generate it."
            ),
        )

    log.info("[/download] Serving file: %s", output_path.resolve())
    return FileResponse(
        path=str(output_path.resolve()),
        filename=cfg.OUTPUT_FILENAME,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )