# runeLoLDB

A League of Legends desktop companion app that **automatically recommends and imports the best rune page during champion select**.

## Features

- 🔍 **Detects champion select** via the League Client API (LCU)
- 🧠 **Three-layer recommendation engine**:
  1. **Player History** — runes you've used and won with in this exact matchup
  2. **Champion Default** — curated default rune pages per champion/role
  3. **Pro / High-Elo Data** — aggregated statistics from Master+ games
- 📊 **Learning system** — every match result is stored so the app improves over time
- ⚡ **One-click rune import** — imports the recommended page directly into the LoL client
- 🖥️ **Always-on-top overlay** — shown during champion select, hidden otherwise
- 📈 **Matchup stats** — win rate, difficulty rating, and sample sizes

---

## Architecture

```
League Client (LCU)
       │
       ▼
Electron Overlay (TypeScript)
       │  IPC / HTTP
       ▼
FastAPI Backend (Python)
       │
       ├── Layer 1: Player Rune Memory (PostgreSQL)
       ├── Layer 2: Default Rune Database (PostgreSQL)
       └── Layer 3: High-Elo Rune Statistics (PostgreSQL)
       │
       ▼
    PostgreSQL
```

---

## Tech Stack

| Layer    | Technology |
|----------|------------|
| Frontend | Electron + TypeScript |
| Backend  | Python + FastAPI |
| Database | PostgreSQL |
| Tests    | Jest (frontend) · pytest (backend) |

---

## Project Structure

```
runeLoLDB/
├── frontend/               # Electron + TypeScript overlay
│   ├── src/
│   │   ├── main/           # Electron main process
│   │   │   ├── index.ts              # App entry & window management
│   │   │   ├── leagueClientPoller.ts # Champion-select polling
│   │   │   ├── backendClient.ts      # Backend HTTP client
│   │   │   └── preload.ts            # Context-bridge API
│   │   ├── renderer/       # Overlay UI
│   │   │   ├── index.ts    # Renderer entry point
│   │   │   ├── overlay.ts  # HTML renderer (pure function)
│   │   │   └── styles.css
│   │   └── shared/
│   │       └── types.ts    # Shared TypeScript types
│   ├── public/index.html
│   ├── package.json
│   └── tsconfig.json
│
├── backend/                # Python FastAPI backend
│   ├── main.py             # Application entry point
│   ├── app/
│   │   ├── api/
│   │   │   ├── runes.py    # Rune recommendation & management endpoints
│   │   │   ├── matches.py  # Match result recording
│   │   │   ├── champions.py
│   │   │   └── lcu.py      # League Client proxy endpoints
│   │   ├── services/
│   │   │   ├── rune_recommender.py  # Three-layer recommendation algorithm
│   │   │   └── league_client.py     # LCU API wrapper
│   │   ├── models.py       # SQLAlchemy ORM models
│   │   ├── schemas.py      # Pydantic request/response schemas
│   │   └── database.py     # DB connection & session management
│   ├── tests/              # pytest test suite
│   ├── requirements.txt
│   └── Dockerfile
│
├── database/
│   ├── migrations/
│   │   ├── 001_initial_schema.sql   # Table definitions
│   │   └── 002_seed_data.sql        # Champion & default rune seed data
│   └── migrate.py          # Migration runner
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) ≥ 20
- [Python](https://python.org/) ≥ 3.11
- [PostgreSQL](https://www.postgresql.org/) ≥ 14 **or** [Docker](https://docker.com/)

### 1 — Clone & configure

```bash
git clone https://github.com/Qrytics/runeLoLDB.git
cd runeLoLDB
cp .env.example .env          # edit as needed
```

### 2 — Start the database

**With Docker (recommended):**

```bash
docker-compose up -d db
```

**Without Docker:**

```bash
createdb runeloldb
python database/migrate.py
```

### 3 — Start the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# API available at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

### 4 — Start the Electron overlay

```bash
cd frontend
npm install
npm run dev
```

The overlay window appears automatically. It detects champion select and displays the recommended rune page.

---

## Docker (all-in-one)

```bash
docker-compose up --build
```

Then start the Electron frontend separately (it must run on your local machine to interact with the League client):

```bash
cd frontend && npm install && npm start
```

---

## Running Tests

### Backend

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

### Frontend

```bash
cd frontend
npm test
```

---

## Rune Recommendation Algorithm

```
Champion Select Detected
         │
         ▼
 ┌──────────────────────────────┐
 │ Layer 1 — Player History     │
 │ Matchup: Champion vs Enemy   │
 │ Prefer pages with wins       │
 └──────────────────┬───────────┘
                    │ no history
                    ▼
 ┌──────────────────────────────┐
 │ Layer 2 — Default Rune Page  │
 │ Champion + Role specific     │
 └──────────────────┬───────────┘
                    │ no default
                    ▼
 ┌──────────────────────────────┐
 │ Layer 3 — Pro / High-Elo     │
 │ Highest win rate + pick rate │
 │ from Master+ games           │
 └──────────────────┬───────────┘
                    │
                    ▼
         Overlay displayed
         with source label
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/runes/recommend` | Get a rune recommendation |
| `POST` | `/api/runes/player` | Save a player rune page |
| `GET`  | `/api/runes/player/{player_id}` | List player rune history |
| `POST` | `/api/runes/default` | Create/update a default rune page |
| `GET`  | `/api/runes/default/{champion_id}` | Get default rune pages for a champion |
| `POST` | `/api/runes/pro` | Ingest pro rune statistics |
| `POST` | `/api/matches` | Record a match result |
| `GET`  | `/api/champions` | List all champions |
| `GET`  | `/lcu/champ-select` | Proxy: current champ-select session |
| `POST` | `/lcu/runes/import` | Proxy: import rune page into client |
| `GET`  | `/health` | Health check |

Interactive API documentation is available at `http://localhost:8000/docs` when the backend is running.

---

## Database Schema

| Table | Purpose |
|-------|---------|
| `champions` | Champion metadata (id, name, key) |
| `player_runes` | Player rune history with win/loss outcomes |
| `default_runes` | Curated default rune pages per champion/role |
| `pro_runes` | High-elo aggregated rune statistics |
| `matchup_stats` | Matchup difficulty and win-rate data |

---

## License

MIT
