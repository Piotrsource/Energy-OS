# AI Energy Optimization Platform

Backend API + React dashboard for AI-driven energy optimization in hotels and commercial buildings. Monitors IoT sensor data, generates consumption forecasts with ML models, and provides actionable HVAC/lighting recommendations.

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│   Frontend   │────►│   Backend    │────►│   TimescaleDB    │
│  React+Nginx │     │   FastAPI    │     │  PostgreSQL 16   │
│  port 3000   │     │  port 8000   │     │  port 5433       │
└──────────────┘     └──────────────┘     └──────────────────┘
```

**Tech Stack:**
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Recharts
- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Alembic
- **Database:** PostgreSQL 16 + TimescaleDB (time-series hypertables)
- **Auth:** JWT (HS256) + bcrypt password hashing
- **Infra:** Docker Compose, nginx reverse proxy

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose v2+

### 1. Clone and configure

```bash
cp .env.example .env
# Edit .env if needed (defaults work for local development)
```

### 2. Start everything

```bash
docker compose up --build
```

This starts three containers:
- **db** — TimescaleDB on port 5433
- **api** — FastAPI on port 8000
- **frontend** — React dashboard on port 3000

### 3. Run database migrations

```bash
docker compose exec api alembic upgrade head
```

### 4. Seed demo data (optional)

```bash
docker compose exec api python /app/scripts/seed_demo_data.py
```

### 5. Open the app

| URL | Description |
|-----|-------------|
| http://localhost:3000 | React Dashboard |
| http://localhost:8000/docs | Swagger API Docs |
| http://localhost:8000/redoc | ReDoc API Docs |

### Default Login

```
Email:    admin@energyplatform.local
Password: admin123
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/login` | Authenticate, get JWT token |
| GET/POST | `/api/v1/buildings` | List / create buildings |
| GET/PATCH/DELETE | `/api/v1/buildings/{id}` | Get / update / delete building |
| GET/POST | `/api/v1/zones` | List / create zones |
| POST | `/api/v1/sensors/readings` | Bulk insert sensor data |
| GET | `/api/v1/sensors/readings` | Query sensor data |
| POST | `/api/v1/hvac/status` | Bulk insert HVAC status |
| GET | `/api/v1/hvac/status` | Query HVAC status |
| POST | `/api/v1/energy-meters/readings` | Bulk insert meter data |
| GET | `/api/v1/energy-meters/readings` | Query meter data |
| GET/POST | `/api/v1/forecasts` | List / create AI forecasts |
| GET/POST/PATCH | `/api/v1/recommendations` | Manage AI recommendations |
| GET | `/api/v1/buildings/{id}/energy-summary` | Energy analytics |
| GET | `/api/v1/buildings/{id}/carbon-emissions` | Carbon analytics |
| GET | `/api/v1/anomalies` | Anomaly detection |

## Running Tests

```bash
cd backend
pip install -e ".[dev]"
pytest -v
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Async PostgreSQL URL (asyncpg) | `postgresql+asyncpg://energy_user:energy_pass_dev@db:5432/energy_platform` |
| `DATABASE_URL_SYNC` | Sync PostgreSQL URL (psycopg2, for Alembic) | `postgresql+psycopg2://energy_user:energy_pass_dev@db:5432/energy_platform` |
| `JWT_SECRET_KEY` | JWT signing secret (change in prod!) | `CHANGE-ME-IN-PRODUCTION` |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime | `60` |
| `APP_NAME` | Application display name | `AI Energy Optimization Platform` |
| `DEBUG` | Enable SQL query logging | `false` |
| `LOG_LEVEL` | Python log level | `info` |

## Project Structure

```
├── docker-compose.yml          # Orchestrates all services
├── .env / .env.example         # Environment configuration
├── backend/
│   ├── Dockerfile              # Multi-stage Python image
│   ├── pyproject.toml          # Python dependencies
│   ├── alembic.ini             # Migration config
│   ├── alembic/versions/       # Database migrations
│   ├── app/
│   │   ├── main.py             # FastAPI application
│   │   ├── config.py           # Settings (pydantic-settings)
│   │   ├── api/v1/             # Route handlers
│   │   ├── auth/               # JWT, passwords, RBAC
│   │   ├── db/                 # Engine, session, base
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic request/response
│   │   └── services/           # Business logic
│   └── tests/                  # Pytest test suite
├── frontend/
│   ├── Dockerfile              # Multi-stage Node+nginx image
│   ├── nginx.conf              # Reverse proxy config
│   └── src/                    # React application
└── scripts/
    ├── init_db.sql             # TimescaleDB extension setup
    └── seed_demo_data.py       # Demo data generator
```
