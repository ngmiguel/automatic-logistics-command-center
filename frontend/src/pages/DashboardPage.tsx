import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Truck, Activity, AlertTriangle, Gauge, Fuel, Zap } from 'lucide-react';
import { analyticsApi, trackingApi } from '@/api/services';
import { FleetGlobe } from '@/components/3d/FleetGlobe';
import { StatCard } from '@/components/ui/StatCard';
import { PageTransition } from '@/components/ui/PageTransition';
import { useWebSocket } from '@/hooks/useWebSocket';
import type { Telemetry } from '@/types';

export function DashboardPage() {
  const { data: summary } = useQuery({
    queryKey: ['analytics-summary'],
    queryFn: () => analyticsApi.summary().then((r) => r.data),
    refetchInterval: 5000,
  });

  const { data: liveTelemetry = [] } = useQuery({
    queryKey: ['telemetry-live'],
    queryFn: () => trackingApi.live().then((r) => r.data),
    refetchInterval: 3000,
  });

  const { messages } = useWebSocket('/ws/dashboard');
  const wsTelemetry = messages
    .filter((m) => m.channel?.includes('telemetry'))
    .slice(0, 20)
    .map((m) => m.data as Telemetry);

  const fleet = summary?.fleet;

  return (
    <PageTransition className="p-6 space-y-6">
      <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}>
        <h1 className="font-display text-2xl font-bold tracking-wide">Command Center</h1>
        <p className="text-gray-500 text-sm mt-1">Real-time global fleet operations</p>
      </motion.div>

      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
        <StatCard title="Total Fleet" value={fleet?.total_vehicles ?? '—'} icon={Truck} delay={0.1} />
        <StatCard title="En Route" value={fleet?.en_route_vehicles ?? '—'} icon={Activity} color="green" delay={0.15} />
        <StatCard title="Incidents" value={fleet?.incident_vehicles ?? '—'} icon={AlertTriangle} color="red" delay={0.2} />
        <StatCard title="Utilization" value={fleet ? `${(fleet.fleet_utilization_rate * 100).toFixed(1)}%` : '—'} icon={Gauge} color="purple" delay={0.25} />
        <StatCard title="Avg Fuel" value={fleet ? `${fleet.average_fuel_level.toFixed(1)}%` : '—'} icon={Fuel} color="amber" delay={0.3} />
        <StatCard title="Avg Speed" value={fleet ? `${fleet.average_speed_kmh.toFixed(0)} km/h` : '—'} icon={Zap} delay={0.35} />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
          className="glass-panel glow-border h-[420px] overflow-hidden relative"
        >
          <div className="absolute top-4 left-4 z-10">
            <h2 className="font-display text-sm tracking-wider text-blue-400">3D FLEET GLOBE</h2>
            <p className="text-xs text-gray-500">{liveTelemetry.length} vehicles tracked</p>
          </div>
          <FleetGlobe telemetry={liveTelemetry} className="h-full" />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="glass-panel glow-border p-5"
        >
          <h2 className="font-display text-sm tracking-wider text-blue-400 mb-4">LIVE TELEMETRY</h2>
          <div className="space-y-2 max-h-[360px] overflow-y-auto font-mono text-xs">
            {(wsTelemetry.length ? wsTelemetry : liveTelemetry.slice(0, 15)).map((t, i) => (
              <motion.div
                key={`${t.vehicle_id}-${i}`}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-center gap-3 py-2 border-b border-alcc-border/50"
              >
                <span className="text-blue-400 w-20 truncate">{t.vehicle_id.slice(0, 8)}</span>
                <span className="text-gray-400">{t.latitude.toFixed(2)}, {t.longitude.toFixed(2)}</span>
                <span className="text-green-400 ml-auto">{t.speed_kmh.toFixed(0)} km/h</span>
                <span className={`px-2 py-0.5 rounded text-[10px] ${
                  t.state === 'en_route' ? 'bg-green-500/20 text-green-400' :
                  t.state === 'incident' ? 'bg-red-500/20 text-red-400' : 'bg-blue-500/20 text-blue-400'
                }`}>{t.state}</span>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </PageTransition>
  );
}
