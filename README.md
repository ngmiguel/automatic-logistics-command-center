# Automatic Logistics Command Center

> Real-time autonomous fleet simulation platform — Clean Architecture, DDD, Event-Driven Design.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

**Automatic Logistics Command Center (ALCC)** simulates a worldwide autonomous transport company operating **1,000 virtual vehicles**. Each vehicle moves, consumes fuel, generates incidents, receives missions, and streams real-time telemetry — without any physical hardware.

The platform provides fleet operators and dispatchers with a live command dashboard and lays the foundation for future AI-driven optimization (routing, fuel, maintenance).

## Architecture (Target)

```
┌─────────────────┐     WebSocket      ┌──────────────┐
│  1000 Vehicles  │ ─────────────────► │    Redis     │
│   (Simulator)   │                    │  Pub/Sub +   │
└─────────────────┘                    │    Cache     │
                                       └──────┬───────┘
                                              │
                                       ┌──────▼───────┐
                                       │   FastAPI    │
                                       │  API Gateway │
                                       └──────┬───────┘
                                              │
                              ┌───────────────┼───────────────┐
                              │               │               │
                        Dashboard        PostgreSQL        Celery
                       (Real-time)       (Persistence)    (Async Jobs)
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| API | FastAPI, JWT |
| Real-time | WebSockets, Redis Pub/Sub |
| Persistence | PostgreSQL |
| Async tasks | Celery |
| Testing | Pytest (unit, integration, E2E) |
| DevOps | Docker, GitHub Actions, Kubernetes-ready |

## Domain Model (Bounded Contexts)

| Context | Responsibility |
|---------|----------------|
| **Auth** | Authentication, authorization, RBAC |
| **Fleet** | Vehicles, virtual drivers, fleet lifecycle |
| **Tracking** | GPS telemetry, speed, vehicle state (1 Hz) |
| **Routing** | Missions, route assignment, optimization |
| **Notification** | Alerts, incidents, event delivery |
| **Analytics** | KPIs, dashboards, reporting |

## Project Status

| Phase | Status |
|-------|--------|
| Design & Architecture | 🔄 In progress |
| Core Implementation | ⏳ Planned |
| Real-time Pipeline | ⏳ Planned |
| CI/CD & Docker | ⏳ Planned |
| Kubernetes Deployment | ⏳ Planned |

## Documentation

All design artifacts live under [`docs/`](docs/):

```
docs/
├── design/          # Business analysis, event storming, use cases
└── architecture/    # Domain models, infra, security, deployment
```

## Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Stable documentation and releases |
| `develop` | Active design and implementation work |

## Author

**Miguel** — [GitHub @ngmiguel](https://github.com/ngmiguel)

## License

MIT — see [LICENSE](LICENSE) for details.
