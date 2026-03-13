# Oura Ring Analytics Dashboard

A full-stack health analytics dashboard that pulls data from the Oura Ring API v2 and visualizes sleep, HRV, readiness, and activity metrics with trend analysis and cross-metric correlations.

## Features

- **Sleep Dashboard** — nightly sleep score, stage breakdown (REM/deep/light), sleep efficiency, latency, and timing trends
- **HRV & Readiness** — readiness score timeline, HRV balance trend, resting heart rate
- **Activity** — daily steps, active calories, activity score, activity breakdown by intensity
- **Correlations Panel** — Pearson correlation matrix across 10 health metrics
- **Date Range Selector** — toggle between 7 / 30 / 90 day windows

## Prerequisites

- Python 3.10+
- Node.js 18+
- An Oura personal access token ([get one here](https://cloud.ouraring.com/personal-access-tokens))

## Setup

### Backend

```bash
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure your Oura API token
cp .env.example .env
# Edit .env and add your OURA_API_TOKEN

# Start the server
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The dashboard will be available at `http://localhost:5173`. The Vite dev server proxies `/api` requests to the backend automatically.

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /api/sleep?days=7` | Sleep scores, stages, efficiency |
| `GET /api/readiness?days=7` | Readiness scores, HRV, heart rate |
| `GET /api/activity?days=7` | Steps, calories, activity breakdown |
| `GET /api/heartrate?days=7` | Heart rate data (auto-downsampled) |
| `GET /api/correlations?days=30` | Cross-metric correlation matrix |

All endpoints accept a `days` query parameter (1-90, default 7).

## Tech Stack

- **Backend**: FastAPI, httpx, numpy, Pydantic
- **Frontend**: React, Recharts, Tailwind CSS v4, Vite
