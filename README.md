# Automatic Logistics Command Center

> Real-time autonomous fleet simulation platform — Clean Architecture, DDD, Event-Driven Design.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

**Automatic Logistics Command Center (ALCC)** simulates a worldwide autonomous transport company operating **1,000 virtual vehicles**. Each vehicle moves, consumes fuel, generates incidents, receives missions, and streams real-time telemetry at **1 Hz** — without any physical hardware.

## Features

| Module | Capabilities |
|--------|-------------|
| **Auth** | JWT authentication, RBAC (Admin, Operator, Dispatcher, Analyst) |
| **Fleet** | Vehicle CRUD, virtual drivers, state management, fleet stats |
| **Routing** | Mission creation, vehicle assignment, dispatch, completion |
| **Tracking** | Live telemetry, history, Redis-cached positions |
| **Simulator** | 1000-vehicle engine: movement, fuel, probabilistic incidents |
| **WebSocket** | Real-time dashboard feed via Redis Pub/Sub |
| **Notifications** | Alerts, incident tracking, resolution workflow |
| **Analytics** | Fleet/mission/incident KPIs, full dashboard summary |
| **Celery** | Async route optimization, maintenance scheduling, analytics |
| **Dashboard** | Built-in HTML command center with live KPIs |
| **DevOps** | Docker Compose, GitHub Actions CI, Prometheus metrics |

## Architecture

```
1000 Vehicles (Simulator) ──► Redis Pub/Sub ──► WebSocket ──► Dashboard
                                      │
                                 FastAPI Gateway
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
               PostgreSQL          Celery           JWT Auth
              (Persistence)      (Async Jobs)      (RBAC)
```

## Quick Start

### Docker (recommended)

```bash
cp .env.example .env
docker compose up --build
```

Open [http://localhost:8000](http://localhost:8000) for the command center dashboard.

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Local Development

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pip install -e .

# Start PostgreSQL + Redis (or use docker compose up postgres redis)
cp .env.example .env
python scripts/seed_users.py

uvicorn alcc.main:app --reload --app-dir src
```

### Default Users

| Email | Password | Role |
|-------|----------|------|
| admin@alcc.io | admin1234 | Admin |
| dispatcher@alcc.io | dispatch123 | Dispatcher |
| operator@alcc.io | operator123 | Operator |
| analyst@alcc.io | analyst123 | Analyst |

## API Endpoints

| Prefix | Description |
|--------|-------------|
| `/api/v1/auth` | Register, login, profile |
| `/api/v1/fleet` | Vehicles, drivers, fleet stats |
| `/api/v1/missions` | Mission lifecycle |
| `/api/v1/tracking` | Telemetry queries, live fleet |
| `/api/v1/notifications` | Alerts and incidents |
| `/api/v1/analytics` | KPIs and dashboard data |
| `/api/v1/tasks` | Celery async task triggers |
| `/ws/dashboard` | WebSocket real-time feed |
| `/health` | Health check |
| `/metrics` | Prometheus metrics |

## Project Structure

```
src/alcc/
├── auth/           # JWT, RBAC
├── fleet/          # Vehicles, virtual drivers
├── routing/        # Missions, dispatch
├── tracking/       # Telemetry
├── notification/   # Alerts, incidents
├── analytics/      # KPIs
├── simulator/      # 1000-vehicle engine
├── worker/         # Celery tasks
└── shared/         # Domain base, DB, Redis, WebSocket
```

## Testing

```bash
pytest tests/ -v --cov=alcc
```

## Documentation

```
docs/
├── design/
│   └── 01-business-analysis.md
└── architecture/
```

## Author

**Miguel** — [GitHub @ngmiguel](https://github.com/ngmiguel)

## License

MIT — see [LICENSE](LICENSE) for details.
