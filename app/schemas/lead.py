"""
app/schemas/lead.py

Pydantic models for request/response validation.
"""

from __future__ import annotations

from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator


# ─── Lead schema ──────────────────────────────────────────────────────────────

class Lead(BaseModel):
    """A single normalised, validated B2B lead."""

    name:    str = Field("", description="Contact or business name")
    company: str = Field("", description="Company / organisation name")
    phone:   str = Field("", description="Normalised phone number (E.164, e.g. +91XXXXXXXXXX)")
    email:   str = Field("", description="Email address")
    website: str = Field("", description="Website URL or LinkedIn profile URL")
    city:    str = Field("", description="City where the lead is located")
    source:  Literal["google_maps", "linkedin"] = Field(
        ..., description="Which scraper produced this lead"
    )

    model_config = {"from_attributes": True}


# ─── Request schemas ──────────────────────────────────────────────────────────

class ScrapeRequest(BaseModel):
    """Body for POST /scrape."""

    queries: list[str] = Field(
        default_factory=list,
        description=(
            "Google Maps search strings "
            "(e.g. 'gyms in Delhi'). "
            "Falls back to config.GOOGLE_MAPS_QUERIES when empty."
        ),
        examples=[["gyms in Delhi", "restaurants in Mumbai"]],
    )

    linkedin_searches: list[dict] = Field(
        default_factory=list,
        description=(
            "LinkedIn search configs (keys: keywords, location, max_results). "
            "Falls back to config.LINKEDIN_SEARCHES when empty."
        ),
        examples=[[{"keywords": "CTO", "location": "Bangalore", "max_results": 10}]],
    )

    include_leads_preview: bool = Field(
        False,
        description="When True, the first 20 leads are included in the response body.",
    )

    @field_validator("queries", mode="before")
    @classmethod
    def _strip_queries(cls, v: list[str]) -> list[str]:
        return [q.strip() for q in v if q.strip()]


# ─── Response schemas ─────────────────────────────────────────────────────────

class PipelineStats(BaseModel):
    """Counters from a single pipeline run."""

    google_maps_raw:  int = Field(description="Raw records from Google Maps scraper")
    linkedin_raw:     int = Field(description="Raw records from LinkedIn scraper")
    parsed:           int = Field(description="Leads after parsing")
    valid:            int = Field(description="Leads that passed validation")
    rejected:         int = Field(description="Leads rejected by validator")
    duplicates_removed: int = Field(description="Duplicates removed")
    unique:           int = Field(description="Final unique lead count")


class ScrapeResponse(BaseModel):
    """Response body for POST /scrape."""

    status:      str          = Field("success")
    total_leads: int          = Field(description="Number of unique leads exported")
    output_file: str          = Field(description="Absolute path of the saved Excel file")
    stats:       PipelineStats
    leads:       Optional[list[Lead]] = Field(
        None,
        description="Preview of first 20 leads (only when include_leads_preview=True)",
    )


class HealthResponse(BaseModel):
    """Response body for GET /health."""

    status:       str = "ok"
    apify_token_set: bool = Field(description="Whether APIFY_API_TOKEN is configured")