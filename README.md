# Health Dashboard

A full-stack health analytics dashboard that combines Oura Ring API v2 data with Apple Health exports. Visualizes sleep, HRV, readiness, activity, heart rate, workouts, and vitals with trend analysis and cross-metric correlations.

## Features

### Oura Ring
- **Sleep Dashboard** — nightly sleep score, stage breakdown (REM/deep/light), sleep efficiency, latency, and timing trends
- **HRV & Readiness** — readiness score timeline, HRV balance trend, resting heart rate
- **Activity** — daily steps, active calories, activity score, activity breakdown by intensity

### Apple Health
- **Heart** — heart rate trends (avg/min/max), resting HR, HRV (SDNN)
- **Sleep** — sleep stages from Apple Watch (core/deep/REM/awake)
- **Activity** — daily steps, distance, flights climbed, active + basal energy
- **Workouts** — workout history with type breakdown
- **Vitals** — respiratory rate, blood oxygen (SpO2)

### Cross-source
- **Correlations Panel** — Pearson correlation matrix across 15 metrics from both data sources
- **Date Range Selector** — 7d / 30d / 90d / 1y / All

## Prerequisites

- Python 3.10+
- Node.js 18+
- An Oura personal access token ([get one here](https://cloud.ouraring.com/personal-access-tokens))
- Apple Health export (optional — export from iPhone Health app > profile > Export All Health Data)

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

### Apple Health Data

Place your Apple Health export in `apple_health_export/` at the project root (next to `backend/` and `frontend/`). The backend will automatically parse it on first startup and cache results in a SQLite database. Parsing ~9M records takes about 30 seconds.

To re-parse: `POST /api/apple/parse`
Check status: `GET /api/apple/parse/status`

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The dashboard will be available at `http://localhost:5173`.

## API Endpoints

### Oura Ring

| Endpoint | Description |
|---|---|
| `GET /api/sleep?days=7` | Sleep scores, stages, efficiency |
| `GET /api/readiness?days=7` | Readiness scores, HRV, heart rate |
| `GET /api/activity?days=7` | Steps, calories, activity breakdown |
| `GET /api/heartrate?days=7` | Heart rate data (auto-downsampled) |

### Apple Health

| Endpoint | Description |
|---|---|
| `GET /api/apple/heart-rate?days=30` | Daily avg/min/max heart rate |
| `GET /api/apple/hrv?days=30` | Daily HRV (SDNN) |
| `GET /api/apple/resting-hr?days=30` | Resting heart rate trend |
| `GET /api/apple/sleep?days=30` | Sleep stages per night |
| `GET /api/apple/steps?days=30` | Steps, distance, flights |
| `GET /api/apple/energy?days=30` | Active + basal calories |
| `GET /api/apple/workouts?days=90` | Workout history + type breakdown |
| `GET /api/apple/respiratory?days=30` | Respiratory rate |
| `GET /api/apple/spo2?days=30` | Blood oxygen |

### Cross-source

| Endpoint | Description |
|---|---|
| `GET /api/correlations?days=30` | Cross-metric correlation matrix |

Apple Health endpoints support `days=0` for all historical data. Ranges >90 days return weekly aggregates.

## Tech Stack

- **Backend**: FastAPI, httpx, numpy, SQLite, Pydantic
- **Frontend**: React, Recharts, Tailwind CSS v4, Vite
