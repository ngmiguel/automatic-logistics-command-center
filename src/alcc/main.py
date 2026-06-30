from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
from starlette.responses import Response

from alcc.analytics.presentation.routes import router as analytics_router
from alcc.auth.presentation.routes import router as auth_router
from alcc.config import get_settings
from alcc.fleet.presentation.routes import router as fleet_router
from alcc.notification.presentation.routes import router as notification_router
from alcc.routing.presentation.routes import router as routing_router
from alcc.shared.infrastructure.database.session import init_db
from alcc.shared.infrastructure.logging import setup_logging
from alcc.shared.infrastructure.redis_client import redis_client
from alcc.shared.presentation.websocket import router as ws_router
from alcc.shared.presentation.websocket import start_ws_listener
from alcc.simulator.engine import simulator
from alcc.tracking.presentation.routes import router as tracking_router
from alcc.worker.presentation.routes import router as tasks_router

settings = get_settings()
setup_logging(settings.debug)

REQUEST_COUNT = Counter("alcc_http_requests_total", "Total HTTP requests", ["method", "endpoint"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    if not settings.testing:
        await redis_client.connect()
        await init_db()
        await simulator.seed_fleet()
        await simulator.start()
        start_ws_listener()
    else:
        await init_db()
    yield
    if not settings.testing:
        await simulator.stop()
        await redis_client.disconnect()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Autonomous fleet simulation command center",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = settings.api_prefix
app.include_router(auth_router, prefix=api)
app.include_router(fleet_router, prefix=api)
app.include_router(routing_router, prefix=api)
app.include_router(tracking_router, prefix=api)
app.include_router(notification_router, prefix=api)
app.include_router(analytics_router, prefix=api)
app.include_router(tasks_router, prefix=api)
app.include_router(ws_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "healthy", "service": settings.app_name, "version": "0.1.0"}


@app.get("/metrics")
async def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/", response_class=HTMLResponse)
async def dashboard() -> str:
    return DASHBOARD_HTML


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ALCC — Command Center</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0a0e17; color: #e0e6ed; }
  header { background: #111827; padding: 1rem 2rem; border-bottom: 1px solid #1f2937;
           display: flex; justify-content: space-between; align-items: center; }
  header h1 { font-size: 1.4rem; color: #60a5fa; }
  .status { display: flex; gap: 1rem; align-items: center; }
  .dot { width: 10px; height: 10px; border-radius: 50%; background: #22c55e;
         animation: pulse 2s infinite; }
  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
          gap: 1rem; padding: 1.5rem 2rem; }
  .card { background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 1.2rem; }
  .card h3 { font-size: 0.85rem; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.05em; }
  .card .value { font-size: 2rem; font-weight: 700; margin-top: 0.5rem; color: #f9fafb; }
  .card .sub { font-size: 0.8rem; color: #6b7280; margin-top: 0.3rem; }
  .feed { padding: 0 2rem 2rem; }
  .feed h2 { font-size: 1.1rem; margin-bottom: 1rem; color: #d1d5db; }
  #telemetry-feed { max-height: 400px; overflow-y: auto; background: #111827;
                    border: 1px solid #1f2937; border-radius: 12px; padding: 1rem; }
  .entry { padding: 0.4rem 0; border-bottom: 1px solid #1f2937; font-size: 0.85rem;
           font-family: 'Cascadia Code', monospace; color: #9ca3af; }
  .entry .vid { color: #60a5fa; }
  .entry .spd { color: #34d399; }
</style>
</head>
<body>
<header>
  <h1>Automatic Logistics Command Center</h1>
  <div class="status"><div class="dot"></div><span id="conn-status">Connecting...</span></div>
</header>
<div class="grid">
  <div class="card"><h3>Total Vehicles</h3><div class="value" id="kpi-total">—</div></div>
  <div class="card"><h3>En Route</h3><div class="value" id="kpi-enroute">—</div></div>
  <div class="card"><h3>Incidents</h3><div class="value" id="kpi-incidents">—</div></div>
  <div class="card"><h3>Utilization</h3><div class="value" id="kpi-util">—</div></div>
  <div class="card"><h3>Avg Fuel</h3><div class="value" id="kpi-fuel">—</div><div class="sub">%</div></div>
  <div class="card"><h3>Avg Speed</h3><div class="value" id="kpi-speed">—</div><div class="sub">km/h</div></div>
</div>
<div class="feed">
  <h2>Live Telemetry Feed</h2>
  <div id="telemetry-feed"></div>
</div>
<script>
const feed = document.getElementById('telemetry-feed');
const ws = new WebSocket(`ws://${location.host}/ws/dashboard`);
let msgCount = 0;
ws.onopen = () => { document.getElementById('conn-status').textContent = 'Live'; };
ws.onclose = () => { document.getElementById('conn-status').textContent = 'Disconnected'; };
ws.onmessage = (e) => {
  const msg = JSON.parse(e.data);
  if (msg.channel && msg.channel.includes('telemetry')) {
    const d = msg.data;
    msgCount++;
    if (msgCount % 50 === 0) {
      const el = document.createElement('div');
      el.className = 'entry';
      el.innerHTML = `<span class="vid">${d.vehicle_id.slice(0,8)}</span> `
        + `lat ${d.latitude.toFixed(4)} lng ${d.longitude.toFixed(4)} `
        + `<span class="spd">${d.speed_kmh.toFixed(1)} km/h</span> `
        + `fuel ${d.fuel_level.toFixed(1)}% [${d.state}]`;
      feed.prepend(el);
      if (feed.children.length > 100) feed.lastChild.remove();
    }
  }
};
async function refreshKPIs() {
  try {
    const r = await fetch('/api/v1/analytics/public/summary');
    if (!r.ok) return;
    const summary = await r.json();
    const d = summary.fleet;
    document.getElementById('kpi-total').textContent = d.total_vehicles;
    document.getElementById('kpi-enroute').textContent = d.en_route_vehicles;
    document.getElementById('kpi-incidents').textContent = d.incident_vehicles;
    document.getElementById('kpi-util').textContent = (d.fleet_utilization_rate * 100).toFixed(1) + '%';
    document.getElementById('kpi-fuel').textContent = d.average_fuel_level.toFixed(1);
    document.getElementById('kpi-speed').textContent = d.average_speed_kmh.toFixed(1);
  } catch {}
}
setInterval(refreshKPIs, 5000);
refreshKPIs();
</script>
</body>
</html>"""


def create_app() -> FastAPI:
    return app
