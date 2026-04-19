"""
processing/deduplicator.py

Removes duplicate leads based on composite keys:
  - Primary key:   (normalised name  + normalised phone)   — exact contact match
  - Secondary key: (normalised name  + normalised company) — same person at same org
"""

import re
import logging

log = logging.getLogger(__name__)

_NON_ALNUM = re.compile(r"[^a-z0-9]")


def _key(text: str) -> str:
    """Lowercase and strip non-alphanumeric characters for fuzzy matching."""
    return _NON_ALNUM.sub("", text.lower())


def deduplicate(leads: list[dict]) -> tuple[list[dict], int]:
    """
    Deduplicate a list of lead dicts.

    Args:
        leads: List of validated lead dicts.

    Returns:
        (deduplicated_leads, removed_count)
    """
    seen_phone:   set[str] = set()
    seen_company: set[str] = set()
    unique: list[dict] = []

    for lead in leads:
        name    = _key(lead.get("name",    ""))
        phone   = _key(lead.get("phone",   ""))
        company = _key(lead.get("company", ""))

        phone_key   = f"{name}|{phone}"   if phone   else None
        company_key = f"{name}|{company}" if company else None

        if phone_key and phone_key in seen_phone:
            log.debug("  [Dedup] Duplicate (phone key): %s", lead.get("name"))
            continue

        if company_key and company_key in seen_company:
            log.debug("  [Dedup] Duplicate (company key): %s", lead.get("name"))
            continue

        # New record — register keys
        if phone_key:
            seen_phone.add(phone_key)
        if company_key:
            seen_company.add(company_key)

        unique.append(lead)

    removed = len(leads) - len(unique)
    log.info(
        "[Dedup] %d unique leads  |  %d duplicates removed  (started with %d)",
        len(unique), removed, len(leads),
    )
    return unique, removed
