"""
app/config.py

Centralised settings for the FastAPI application.
All values are loaded from environment variables (or a .env file).
Downstream modules import from here — not directly from os.getenv.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project root
_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=_env_path, override=False)


# ── Apify ─────────────────────────────────────────────────────────────────────

APIFY_API_TOKEN: str = os.getenv("APIFY_API_TOKEN", "")

GOOGLE_MAPS_ACTOR_ID: str = "compass/crawler-google-places"
LINKEDIN_ACTOR_ID:    str = "peakydev/leads-scraper-ppe"


# ── Retry / timeout ───────────────────────────────────────────────────────────

MAX_RETRIES:   int = int(os.getenv("MAX_RETRIES",   "3"))
RETRY_DELAY_S: int = int(os.getenv("RETRY_DELAY_S",  "5"))
TIMEOUT_SECS:  int = int(os.getenv("TIMEOUT_SECS",  "300"))


# ── Google Maps ───────────────────────────────────────────────────────────────

GOOGLE_MAPS_MAX_RESULTS: int = int(os.getenv("GOOGLE_MAPS_MAX_RESULTS", "20"))

_raw_queries = os.getenv(
    "GOOGLE_MAPS_QUERIES",
    "restaurants in Connaught Place Delhi,"
    "gyms in Hauz Khas Delhi,"
    "dental clinics in South Delhi",
)
GOOGLE_MAPS_QUERIES: list[str] = [q.strip() for q in _raw_queries.split(",") if q.strip()]


# ── LinkedIn ──────────────────────────────────────────────────────────────────

LINKEDIN_MAX_RESULTS: int = int(os.getenv("LINKEDIN_MAX_RESULTS", "25"))

LINKEDIN_SEARCHES: list[dict] = [
    {
        "keywords":    os.getenv("LINKEDIN_KEYWORDS_1", "Founder"),
        "location":    os.getenv("LINKEDIN_LOCATION_1", "Mumbai"),
        "max_results": LINKEDIN_MAX_RESULTS,
    },
    {
        "keywords":    os.getenv("LINKEDIN_KEYWORDS_2", "CTO"),
        "location":    os.getenv("LINKEDIN_LOCATION_2", "Bangalore"),
        "max_results": LINKEDIN_MAX_RESULTS,
    },
]


# ── Phone ─────────────────────────────────────────────────────────────────────

DEFAULT_COUNTRY_CODE: str = os.getenv("DEFAULT_COUNTRY_CODE", "+91")


# ── Output ────────────────────────────────────────────────────────────────────

OUTPUT_DIR:      str = os.getenv("OUTPUT_DIR",      "output")
OUTPUT_FILENAME: str = os.getenv("OUTPUT_FILENAME", "leads.xlsx")


# ── Sanity check ─────────────────────────────────────────────────────────────

def _warn_missing() -> None:
    if not APIFY_API_TOKEN:
        import warnings
        warnings.warn(
            "APIFY_API_TOKEN is not set. Scrapers will raise RuntimeError when called.",
            stacklevel=2,
        )

_warn_missing()