# ALCC Frontend

React 18 SPA for the Automatic Logistics Command Center.

## Quick Start

```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # production bundle → dist/
```

Requires the backend API on `http://localhost:8000` (Vite proxies `/api` and `/ws`).

## Architecture

```
src/
├── api/              # Axios + JWT interceptors, all REST services
├── components/
│   ├── 3d/           # React Three Fiber scenes
│   ├── layout/       # Sidebar, AppLayout
│   └── ui/           # StatCard, PageTransition
├── hooks/            # useWebSocket
├── pages/            # One page per bounded context
├── store/            # Zustand auth (persisted)
└── types/            # Shared TypeScript interfaces
```

## 3D Vehicle Models

Procedural silhouettes inspired by premium automotive design (no trademarks):

| Simulator Model | Variant | Style |
|-----------------|---------|-------|
| AutoHauler M5 | executive | Executive sedan (M-Series inspired) |
| AutoVan Z3 | crossover | Urban crossover (X-Drive inspired) |
| AutoTruck X1 | hauler | Autonomous freight (i-Freight inspired) |

## Demo Accounts

| Email | Password |
|-------|----------|
| admin@alcc.io | admin1234 |
| dispatcher@alcc.io | dispatch123 |
| operator@alcc.io | operator123 |

Run `python scripts/seed_users.py` if users don't exist yet.

## Docker

Built and served via nginx when using `docker compose up` (port 3000).
