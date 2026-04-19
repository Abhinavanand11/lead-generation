# LeadForge — B2B Lead Generation Dashboard

A luxury dark-themed React dashboard for the B2B Lead Generation FastAPI backend.

## Tech Stack

- **React 18** + Vite
- **Tailwind CSS** — utility-first styling
- **Framer Motion** — page & card animations
- **Lucide React** — icon library
- **DM Sans** + **Playfair Display** + **JetBrains Mono** — typography

## Project Structure

```
src/
├── components/
│   ├── Sidebar.jsx          # Left nav with health indicator
│   ├── QueryForm.jsx        # Google Maps + LinkedIn query builder
│   ├── LeadTable.jsx        # Sortable leads preview table
│   ├── StatsCard.jsx        # Animated metric cards
│   └── DownloadButton.jsx   # Excel download trigger
├── pages/
│   └── Dashboard.jsx        # Main layout + state orchestration
├── services/
│   └── api.js               # fetch wrappers: scrapeLeads, downloadFile, checkHealth
├── App.jsx
├── main.jsx
└── index.css
```

## Setup

### 1. Install dependencies

```bash
npm install
```

### 2. Configure environment

```bash
cp .env.example .env
```

If your FastAPI backend is on `http://localhost:8000`, you can leave `VITE_API_URL` empty
(Vite proxies `/scrape`, `/download`, `/health` automatically).

If it's on a different host, set:

```
VITE_API_URL=https://your-api.example.com
```

### 3. Start the dev server

```bash
# Start FastAPI backend first
uvicorn app.main:app --reload --port 8000

# Then start the dashboard
npm run dev
```

Open **http://localhost:5173** in your browser.

### 4. Build for production

```bash
npm run build
npm run preview
```

## API Integration

| Function | Endpoint | Description |
|---|---|---|
| `checkHealth()` | `GET /health` | Checks token config + API liveness |
| `scrapeLeads(params)` | `POST /scrape` | Triggers full pipeline |
| `downloadFile()` | `GET /download` | Streams Excel file download |

### Example scrape payload

```js
{
  queries: ['gyms in Delhi', 'restaurants in Mumbai'],
  linkedin_searches: [
    { keywords: 'CTO', location: 'Bangalore', max_results: 25 }
  ],
  include_leads_preview: true
}
```

## Features

- **Query Builder** — Multi-line Google Maps input + collapsible LinkedIn search rows
- **Pipeline Progress** — Animated loading state listing all 6 pipeline steps
- **Stats Cards** — Total leads, Maps vs LinkedIn counts, duplicates removed
- **Lead Table** — Sortable columns, source badges, alternating rows
- **Download** — One-click Excel export with success/error feedback
- **Health Indicator** — Sidebar shows API connectivity status
- **Animations** — Framer Motion fade/slide-in for all major elements
