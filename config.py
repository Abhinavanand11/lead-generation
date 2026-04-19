"""
config.py  (project root shim)

Legacy modules (scraper/, processing/, exporter/) import `config` by bare name.
This shim re-exports everything from app.config so those modules
continue to work without modification.
"""

from app.config import *  # noqa: F401, F403
from app.config import (
    APIFY_API_TOKEN,
    GOOGLE_MAPS_ACTOR_ID,
    LINKEDIN_ACTOR_ID,
    MAX_RETRIES,
    RETRY_DELAY_S,
    TIMEOUT_SECS,
    GOOGLE_MAPS_MAX_RESULTS,
    GOOGLE_MAPS_QUERIES,
    LINKEDIN_MAX_RESULTS,
    LINKEDIN_SEARCHES,
    DEFAULT_COUNTRY_CODE,
    OUTPUT_DIR,
    OUTPUT_FILENAME,
)