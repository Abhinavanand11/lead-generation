# B2B Lead Generation API

A FastAPI service that scrapes Google Maps and LinkedIn via Apify,
normalises, deduplicates, and exports leads to a formatted Excel workbook.

---

## Project Structure

```
project/
├── app/
│   ├── main.py              # FastAPI entrypoint
│   ├── config.py            # Centralised env-based config
│   ├── api/
│   │   └── routes.py        # API endpoints
│   ├── services/
│   │   ├── pipeline.py      # Full pipeline orchestrator
│   │   ├── google_maps.py   # Google Maps service wrapper
│   │   └── linkedin.py      # LinkedIn service wrapper
│   └── schemas/
│       └── lead.py          # Pydantic request/response models
│
├── processing/              # Reused core modules (unchanged logic)
│   ├── parser.py
│   ├── validator.py
│   ├── deduplicator.py
│   └── phone_utils.py
│
├── exporter/
│   └── excel_exporter.py    # Reused Excel export (unchanged logic)
│
├── scraper/
│   ├── google_maps_scraper.py
│   └── linkedin_scraper.py
│
├── scripts/
│   └── run_pipeline.py      # Optional CLI runner
│
├── config.py                # Root shim → delegates to app/config.py
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

Create a `.env` file in the project root:

```env
# Required
APIFY_API_TOKEN=your_apify_token_here

# Optional overrides (shown with defaults)
GOOGLE_MAPS_MAX_RESULTS=20
GOOGLE_MAPS_QUERIES=restaurants in Connaught Place Delhi,gyms in Hauz Khas Delhi
LINKEDIN_MAX_RESULTS=25
LINKEDIN_KEYWORDS_1=Founder
LINKEDIN_LOCATION_1=Mumbai
LINKEDIN_KEYWORDS_2=CTO
LINKEDIN_LOCATION_2=Bangalore
DEFAULT_COUNTRY_CODE=+91
OUTPUT_DIR=output
OUTPUT_FILENAME=leads.xlsx
MAX_RETRIES=3
RETRY_DELAY_S=5
```

---

## Running the API server

```bash
# From the project root
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Interactive docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc:      http://localhost:8000/redoc

---

## API Endpoints

### `GET /health`
Liveness check.

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok",
  "apify_token_set": true
}
```

---

### `POST /scrape`
Run the full pipeline. Uses config defaults when `queries` / `linkedin_searches` are empty.

```bash
# Use config defaults
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{}'
```

```bash
# Custom queries + preview first 20 leads
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "queries": ["gyms in Delhi", "dental clinics in Mumbai"],
    "linkedin_searches": [
      {"keywords": "CTO", "location": "Bangalore", "max_results": 15}
    ],
    "include_leads_preview": true
  }'
```

**Response:**
```json
{
  "status": "success",
  "total_leads": 47,
  "output_file": "/absolute/path/to/output/leads.xlsx",
  "stats": {
    "google_maps_raw": 40,
    "linkedin_raw": 15,
    "parsed": 55,
    "valid": 50,
    "rejected": 5,
    "duplicates_removed": 3,
    "unique": 47
  },
  "leads": [...]   // only present when include_leads_preview=true
}
```

---

### `GET /download`
Download the most recently generated Excel file.

```bash
curl -OJ http://localhost:8000/download
```

Returns `404` if no file has been generated yet. Run `/scrape` first.

---

## CLI Runner (no server needed)

```bash
python scripts/run_pipeline.py
python scripts/run_pipeline.py --queries "cafes in Delhi" "gyms in Mumbai"
python scripts/run_pipeline.py --no-linkedin
```

---

## Excel Output

The exported workbook contains four sheets:

| Sheet              | Contents                                    |
|--------------------|---------------------------------------------|
| All Leads          | Every unique validated lead                 |
| No Website Leads   | Leads without a website — good for outreach |
| Leads With Phone   | Leads that have a normalised phone number   |
| Summary            | Run statistics (counts per source, etc.)    |

---

## Architecture Notes

- **Async-safe**: `/scrape` runs the blocking pipeline in `asyncio.to_thread`
  so the event loop stays responsive for other requests.
- **Zero logic changes**: `processing/`, `exporter/`, and `scraper/` modules
  are used exactly as-is. Only the wiring layer is new.
- **Config shim**: The root `config.py` re-exports everything from `app/config.py`
  so legacy `import config` statements in scrapers continue to work.