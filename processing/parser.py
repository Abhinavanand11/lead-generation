"""
processing/parser.py

Converts raw scraper output into a unified lead schema:
    {
        "name":    str,
        "company": str,
        "phone":   str,   # normalized
        "email":   str,
        "website": str,
        "city":    str,
        "source":  "google_maps" | "linkedin",
    }
"""

import re
import logging
from typing import Any

from processing.phone_utils import normalize_phone

log = logging.getLogger(__name__)

# ─── Shared helpers ───────────────────────────────────────────────────────────

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")


def _clean(value: Any) -> str:
    """Coerce to string and strip whitespace."""
    if value is None:
        return ""
    return str(value).strip()


def _extract_email(raw_emails: Any, raw_text: str = "") -> str:
    """
    Pick the first usable email from:
      - a list of email strings (Apify format)
      - a plain email string
      - a regex scan of arbitrary text
    """
    if isinstance(raw_emails, list):
        for e in raw_emails:
            e = _clean(e)
            if "@" in e:
                return e.lower()
    elif isinstance(raw_emails, str) and "@" in raw_emails:
        return raw_emails.strip().lower()

    # Fallback: scan free text
    m = _EMAIL_RE.search(raw_text)
    return m.group(0).lower() if m else ""


# ─── Google Maps parser ───────────────────────────────────────────────────────

def parse_google_maps_record(raw: dict[str, Any]) -> dict[str, str]:
    """
    Map an Apify Google Maps actor result to the unified lead schema.

    Key fields returned by the actor (subject to version changes):
      title, categoryName, address, city, phone, website,
      emails (list), url, neighborhood, street, postalCode, state
    """
    name    = _clean(raw.get("title") or raw.get("name"))
    company = name   # For business listings, the title IS the company name

    # Phone — actor may return a formatted string
    raw_phone = _clean(raw.get("phone") or raw.get("phoneNumber"))
    phone     = normalize_phone(raw_phone)

    # Email
    email = _extract_email(
        raw.get("emails") or raw.get("email"),
        raw_text=str(raw),
    )

    website = _clean(raw.get("website") or raw.get("websiteUrl") or raw.get("web"))

    # City: prefer dedicated 'city' field, else parse from address
    city = _clean(raw.get("city"))
    if not city:
        address = _clean(raw.get("address"))
        # Address format: "Street, Neighbourhood, City, State Pincode"
        parts = [p.strip() for p in address.split(",")]
        if len(parts) >= 3:
            city = parts[-3]   # third-from-last usually holds the city
        elif parts:
            city = parts[0]

    return {
        "name":    name,
        "company": company,
        "phone":   phone,
        "email":   email,
        "website": website,
        "city":    city,
        "source":  "google_maps",
    }


# ─── LinkedIn parser ──────────────────────────────────────────────────────────

def parse_linkedin_record(raw: dict[str, Any]) -> dict[str, str]:
    """
    Map a LinkedIn scraper result to the unified lead schema.

    Expected input keys: name, company, job_title, linkedin_url, email, phone, city
    The 'job_title' and 'linkedin_url' are LinkedIn-specific and stored in
    'company' and 'website' respectively so that the schema stays consistent.
    """
    name    = _clean(raw.get("name"))
    company = _clean(raw.get("company"))
    phone   = normalize_phone(_clean(raw.get("phone")))
    email   = _extract_email(raw.get("email"), raw_text=str(raw))
    # Store LinkedIn profile URL in website column for easy click-through
    website = _clean(raw.get("linkedin_url") or raw.get("website"))
    city    = _clean(raw.get("city"))

    return {
        "name":    name,
        "company": company,
        "phone":   phone,
        "email":   email,
        "website": website,
        "city":    city,
        "source":  "linkedin",
    }


# ─── Public API ───────────────────────────────────────────────────────────────

def parse_all(
    google_maps_raw: list[dict],
    linkedin_raw: list[dict],
) -> list[dict[str, str]]:
    """
    Parse and combine leads from both sources.

    Returns:
        Combined list of normalized lead dicts.
    """
    leads: list[dict[str, str]] = []

    log.info("[Parser] Parsing %d Google Maps records…", len(google_maps_raw))
    for i, record in enumerate(google_maps_raw):
        try:
            lead = parse_google_maps_record(record)
            leads.append(lead)
        except Exception as exc:  # noqa: BLE001
            log.warning("  [Parser] Skipping Google Maps record #%d: %s", i, exc)

    log.info("[Parser] Parsing %d LinkedIn records…", len(linkedin_raw))
    for i, record in enumerate(linkedin_raw):
        try:
            lead = parse_linkedin_record(record)
            leads.append(lead)
        except Exception as exc:  # noqa: BLE001
            log.warning("  [Parser] Skipping LinkedIn record #%d: %s", i, exc)

    log.info("[Parser] Total parsed leads: %d", len(leads))
    return leads
