"""
processing/phone_utils.py

Phone number cleaning and normalization.
Target format: +91XXXXXXXXXX (10-digit Indian mobile/landline).
"""

import re
import logging

import config

log = logging.getLogger(__name__)

# Digits to strip from the front when we get a local 0XX number
_LEADING_ZERO_RE = re.compile(r"^0+")

# Only digits
_DIGITS_ONLY_RE = re.compile(r"\D")


def _strip_to_digits(raw: str) -> str:
    return _DIGITS_ONLY_RE.sub("", raw)


def normalize_phone(raw: str | None) -> str:
    """
    Normalize a raw phone string to E.164-ish format: +91XXXXXXXXXX.

    Rules applied in order:
      1. Strip whitespace / punctuation.
      2. Remove country code (91 or +91) if already present.
      3. Remove leading 0 (STD trunk prefix).
      4. Accept exactly 10 remaining digits.
      5. Prepend default country code (+91).
      6. Return empty string on failure.
    """
    if not raw:
        return ""

    try:
        digits = _strip_to_digits(raw.strip())

        # Already has country code as digits: 9198765xxxxx or 91xxxxxxxxxx
        if digits.startswith("91") and len(digits) == 12:
            digits = digits[2:]
        elif digits.startswith("91") and len(digits) > 12:
            # e.g. 91 80 4123 5678  → just take last 10
            digits = digits[-10:]

        # Remove leading STD trunk zero
        digits = _LEADING_ZERO_RE.sub("", digits)

        if len(digits) != 10:
            log.debug("  [phone] Could not normalize '%s' (got %d digits)", raw, len(digits))
            return ""

        normalized = f"{config.DEFAULT_COUNTRY_CODE}{digits}"
        log.debug("  [phone] '%s' → '%s'", raw, normalized)
        return normalized

    except Exception as exc:  # noqa: BLE001
        log.warning("  [phone] Error normalizing '%s': %s", raw, exc)
        return ""


def normalize_phone_list(phones: list[str]) -> list[str]:
    """Normalize a list of raw phone strings, dropping blanks."""
    result = []
    for p in phones:
        n = normalize_phone(p)
        if n:
            result.append(n)
    return result
