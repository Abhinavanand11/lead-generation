#  B2B Lead Generation System

A full-stack B2B lead generation platform that scrapes leads from **Google Maps** and **LinkedIn**, processes them, and exports clean data to Excel — with a modern dashboard UI.

---

##  Features

* 🔍 Scrape leads from Google Maps & LinkedIn (via Apify)
* 🧹 Data cleaning, validation & deduplication
* 📞 Phone normalization (+91 format)
* 📊 Excel export with multiple sheets
* ⚡ FastAPI backend (production-ready)
* 🎨 React dashboard (modern dark UI)
* 📥 One-click download of leads

---

##  Project Structure

```
b2b_lead_gen/
│
├── app/                    # FastAPI backend
├── scraper/                # Google Maps & LinkedIn scrapers
├── processing/             # Parser, validator, deduplicator
├── exporter/               # Excel export logic
├── scripts/                # CLI runner
│
├── b2b-dashboard/          # React frontend
│   ├── src/
│   └── package.json
│
├── requirements.txt
├── .env.example
└── README.md
```

---

##  Backend Setup (FastAPI)

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 2. Configure environment

Create `.env` file:

```env
APIFY_API_TOKEN=your_apify_token_here
```

---

### 3. Run server

```bash
uvicorn app.main:app --reload --port 8000
```

---

### 4. API Docs

* Swagger: http://localhost:8000/docs
* Health: http://localhost:8000/health

---

##  Frontend Setup (React Dashboard)

```bash
cd b2b-dashboard
npm install
npm run dev
```

Open:

```
http://localhost:5173
```

---

##  API Endpoints

### ➤ POST `/scrape`

Run scraping pipeline

```json
{
  "queries": ["gyms in Delhi"],
  "linkedin_searches": [
    { "keywords": "Founder", "location": "Delhi", "max_results": 10 }
  ],
  "include_leads_preview": true
}
```

---

### ➤ GET `/download`

Download Excel file

---

### ➤ GET `/health`

Check API status

---

##  Excel Output

Generated file includes:

| Sheet      | Description              |
| ---------- | ------------------------ |
| All Leads  | All unique leads         |
| No Website | Leads without website    |
| With Phone | Leads with phone numbers |
| Summary    | Stats                    |

---

##  Example Usage

### Google Maps queries:

```
digital marketing agency in Delhi
software companies in Bangalore
```

### LinkedIn input:

```json
[
  { "keywords": "Founder", "location": "Delhi", "max_results": 10 }
]
```

---

##  Environment Variables

| Variable        | Description           |
| --------------- | --------------------- |
| APIFY_API_TOKEN | Required for scraping |
| OUTPUT_DIR      | Excel output folder   |
| OUTPUT_FILENAME | Output file name      |

---

##  Tech Stack

### Backend

* FastAPI
* Apify Client
* OpenPyXL
* Pydantic

### Frontend

* React (Vite)
* Tailwind CSS
* Framer Motion
* Lucide Icons

