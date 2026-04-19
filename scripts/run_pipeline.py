#!/usr/bin/env python3
"""
scripts/run_pipeline.py

Optional CLI entry point — runs the pipeline without starting the API server.
Useful for scheduled jobs / cron / quick manual runs.

Usage:
    python scripts/run_pipeline.py
    python scripts/run_pipeline.py --queries "cafes in Delhi" "gyms in Mumbai"
"""

import argparse
import logging
import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main() -> None:
    parser = argparse.ArgumentParser(description="B2B Lead Generation — CLI runner")
    parser.add_argument(
        "--queries", nargs="*",
        help="Google Maps search strings (overrides config defaults)",
    )
    parser.add_argument(
        "--no-linkedin", action="store_true",
        help="Skip LinkedIn scraping",
    )
    args = parser.parse_args()

    from app.services.pipeline import run_pipeline

    result = run_pipeline(
        queries=args.queries or None,
        linkedin_searches=[] if args.no_linkedin else None,
        include_leads=False,
    )

    print(f"\n✅ Done! {result['total_leads']} unique leads → {result['output_file']}")
    print(f"   Google Maps : {result['stats'].google_maps_raw} raw")
    print(f"   LinkedIn    : {result['stats'].linkedin_raw} raw")
    print(f"   Rejected    : {result['stats'].rejected}")
    print(f"   Duplicates  : {result['stats'].duplicates_removed}")


if __name__ == "__main__":
    main()