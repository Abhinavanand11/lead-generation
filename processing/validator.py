"""
processing/validator.py

Quality-gate filtering for leads.

Rules (applied in order):
  1. Must have a non-empty 'name'.
  2. Must have at least one of: phone OR email.
"""

import logging

log = logging.getLogger(__name__)


def validate_leads(leads: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Split leads into valid and rejected sets.

    Args:
        leads: List of parsed lead dicts.

    Returns:
        (valid_leads, rejected_leads)
    """
    valid:    list[dict] = []
    rejected: list[dict] = []

    for lead in leads:
        name  = (lead.get("name") or "").strip()
        phone = (lead.get("phone") or "").strip()
        email = (lead.get("email") or "").strip()

        if not name:
            log.debug("  [Validator] REJECT (no name): %s", lead)
            rejected.append(lead)
            continue

        if not phone and not email:
            log.debug("  [Validator] REJECT (no phone/email): %s", lead)
            rejected.append(lead)
            continue

        valid.append(lead)

    log.info(
        "[Validator] %d valid  |  %d rejected  (total %d)",
        len(valid), len(rejected), len(leads),
    )
    return valid, rejected
