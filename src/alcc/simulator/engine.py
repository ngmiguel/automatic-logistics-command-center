import asyncio
import math
import random
from uuid import UUID

from alcc.config import get_settings
from alcc.fleet.domain.entities import GeoPosition, Vehicle
from alcc.fleet.infrastructure.repositories import VehicleRepository
from alcc.notification.domain.entities import Incident, Notification
from alcc.notification.infrastructure.repositories import IncidentRepository, NotificationRepository
from alcc.routing.domain.entities import Mission
from alcc.routing.infrastructure.repositories import MissionRepository
from alcc.shared.domain.enums import IncidentSeverity, NotificationType, VehicleState
from alcc.shared.infrastructure.database.session import get_session_factory, init_db
from alcc.shared.infrastructure.logging import get_logger
from alcc.shared.infrastructure.redis_client import NOTIFICATION_CHANNEL, redis_client
from alcc.tracking.domain.entities import TelemetrySnapshot
from alcc.tracking.infrastructure.repositories import TelemetryRepository

logger = get_logger(__name__)
settings = get_settings()

WORLD_CITIES = [
    (48.8566, 2.3522),    # Paris
    (40.7128, -74.0060),  # New York
    (35.6762, 139.6503),  # Tokyo
    (51.5074, -0.1278),   # London
    (-33.8688, 151.2093), # Sydney
    (55.7558, 37.6173),   # Moscow
    (-23.5505, -46.6333), # São Paulo
    (28.6139, 77.2090),   # New Delhi
    (31.2304, 121.4737),  # Shanghai
    (1.3521, 103.8198),   # Singapore
    (52.5200, 13.4050),   # Berlin
    (41.9028, 12.4964),   # Rome
    (19.4326, -99.1332),  # Mexico City
    (30.0444, 31.2357),   # Cairo
    (25.2048, 55.2708),   # Dubai
]


class VehicleSimulator:
    """Simulates fleet movement, fuel consumption, and incidents at 1 Hz."""

    def __init__(self) -> None:
        self._running = False
        self._task: asyncio.Task | None = None
        self._destinations: dict[UUID, GeoPosition] = {}

    async def seed_fleet(self, count: int | None = None) -> int:
        count = count or settings.simulator_vehicle_count
        async with get_session_factory()() as session:
            repo = VehicleRepository(session)
            existing = await repo.count()
            if existing >= count:
                logger.info("fleet_already_seeded", count=existing)
                return existing

            to_create = count - existing
            vehicles = []
            for i in range(to_create):
                city = WORLD_CITIES[i % len(WORLD_CITIES)]
                lat = city[0] + random.uniform(-0.5, 0.5)
                lng = city[1] + random.uniform(-0.5, 0.5)
                vehicle = Vehicle(
                    license_plate=f"ALC-{existing + i + 1:04d}",
                    model=random.choice(["AutoTruck X1", "AutoVan Z3", "AutoHauler M5"]),
                    position=GeoPosition(lat, lng),
                    fuel_level=random.uniform(50, 100),
                )
                vehicle.register()
                vehicles.append(vehicle)
            await repo.bulk_save(vehicles)
            await session.commit()
            logger.info("fleet_seeded", created=to_create, total=count)
            return count

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._tick_loop())
        logger.info("simulator_started", interval=settings.simulator_tick_interval_seconds)

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("simulator_stopped")

    async def _tick_loop(self) -> None:
        while self._running:
            try:
                await self._process_tick()
            except Exception as e:
                logger.error("simulator_tick_error", error=str(e))
            await asyncio.sleep(settings.simulator_tick_interval_seconds)

    async def _process_tick(self) -> None:
        async with get_session_factory()() as session:
            vehicle_repo = VehicleRepository(session)
            telemetry_repo = TelemetryRepository(session)
            mission_repo = MissionRepository(session)
            incident_repo = IncidentRepository(session)
            notification_repo = NotificationRepository(session)

            vehicles = await vehicle_repo.get_all(limit=settings.simulator_vehicle_count)

            for vehicle in vehicles:
                if vehicle.state == VehicleState.EN_ROUTE:
                    await self._move_vehicle(vehicle, mission_repo)
                    vehicle.consume_fuel(settings.simulator_fuel_consumption_rate)
                    if random.random() < settings.simulator_incident_rate:
                        await self._trigger_incident(
                            vehicle, incident_repo, notification_repo
                        )
                    if vehicle.fuel_level < 10 and vehicle.fuel_level > 0:
                        await self._notify_low_fuel(vehicle, notification_repo)

                elif vehicle.state == VehicleState.IDLE:
                    vehicle.speed_kmh = 0.0

                snapshot = TelemetrySnapshot.from_vehicle(
                    vehicle.id,
                    vehicle.position.latitude,
                    vehicle.position.longitude,
                    vehicle.speed_kmh,
                    vehicle.fuel_level,
                    vehicle.state,
                )
                await telemetry_repo.save(snapshot)
                await vehicle_repo.save(vehicle)
                await redis_client.publish_telemetry(snapshot.to_dict())

            await session.commit()

    async def _move_vehicle(
        self, vehicle: Vehicle, mission_repo: MissionRepository
    ) -> None:
        if not vehicle.mission_id:
            return
        mission = await mission_repo.get_by_id(vehicle.mission_id)
        if not mission:
            return

        dest = mission.destination
        current = vehicle.position
        speed_kmh = random.uniform(40, 90)
        step_km = speed_kmh / 3600.0

        dist = Mission.haversine_km(
            current.latitude, current.longitude,
            dest.latitude, dest.longitude,
        )
        if dist < step_km:
            vehicle.update_telemetry(dest.latitude, dest.longitude, 0.0)
            vehicle.complete_mission()
            mission.complete()
            await mission_repo.save(mission)
            return

        bearing = math.atan2(
            math.radians(dest.longitude - current.longitude),
            math.radians(dest.latitude - current.latitude),
        )
        lat_step = (step_km / 111.0) * math.cos(bearing)
        lng_step = (step_km / (111.0 * math.cos(math.radians(current.latitude)))) * math.sin(bearing)
        new_lat = current.latitude + math.degrees(lat_step)
        new_lng = current.longitude + math.degrees(lng_step)
        vehicle.update_telemetry(new_lat, new_lng, speed_kmh)

    async def _trigger_incident(
        self,
        vehicle: Vehicle,
        incident_repo: IncidentRepository,
        notification_repo: NotificationRepository,
    ) -> None:
        severity = random.choice(list(IncidentSeverity))
        descriptions = {
            IncidentSeverity.LOW: "Minor sensor anomaly detected",
            IncidentSeverity.MEDIUM: "Tire pressure warning",
            IncidentSeverity.HIGH: "Engine temperature elevated",
            IncidentSeverity.CRITICAL: "Emergency stop triggered",
        }
        vehicle.trigger_incident()
        incident = Incident(
            vehicle_id=vehicle.id,
            severity=severity,
            description=descriptions[severity],
        )
        await incident_repo.save(incident)
        notification = Notification(
            type=NotificationType.INCIDENT,
            title=f"Incident on {vehicle.license_plate}",
            message=incident.description,
            severity=severity,
            vehicle_id=vehicle.id,
        )
        notification.publish()
        await notification_repo.save(notification)
        await redis_client.publish(
            NOTIFICATION_CHANNEL,
            {"title": notification.title, "message": notification.message, "severity": severity.value},
        )

    async def _notify_low_fuel(
        self, vehicle: Vehicle, notification_repo: NotificationRepository
    ) -> None:
        notification = Notification(
            type=NotificationType.LOW_FUEL,
            title=f"Low fuel: {vehicle.license_plate}",
            message=f"Fuel at {vehicle.fuel_level:.1f}%",
            severity=IncidentSeverity.MEDIUM,
            vehicle_id=vehicle.id,
        )
        notification.publish()
        await notification_repo.save(notification)


simulator = VehicleSimulator()
