from alcc.analytics.domain.entities import FleetKPIs, IncidentKPIs, MissionKPIs


class TestAnalyticsDomain:
    def test_fleet_kpis_to_dict(self):
        kpis = FleetKPIs(
            total_vehicles=1000,
            en_route_vehicles=750,
            fleet_utilization_rate=0.75,
            average_fuel_level=65.5,
        )
        data = kpis.to_dict()
        assert data["total_vehicles"] == 1000
        assert data["fleet_utilization_rate"] == 0.75
        assert data["average_fuel_level"] == 65.5
        assert "computed_at" in data

    def test_mission_kpis_to_dict(self):
        kpis = MissionKPIs(total_missions=100, completed=80, completion_rate=0.8)
        data = kpis.to_dict()
        assert data["completed"] == 80
        assert data["completion_rate"] == 0.8

    def test_incident_kpis_to_dict(self):
        kpis = IncidentKPIs(open_incidents=5, critical_incidents=1, incident_rate=0.005)
        data = kpis.to_dict()
        assert data["open_incidents"] == 5
        assert data["critical_incidents"] == 1

    def test_fleet_kpis_rounding(self):
        kpis = FleetKPIs(fleet_utilization_rate=0.756789, average_speed_kmh=45.678)
        data = kpis.to_dict()
        assert data["fleet_utilization_rate"] == 0.7568
        assert data["average_speed_kmh"] == 45.68

    def test_empty_fleet_kpis(self):
        kpis = FleetKPIs()
        data = kpis.to_dict()
        assert data["total_vehicles"] == 0
        assert data["fleet_utilization_rate"] == 0.0
