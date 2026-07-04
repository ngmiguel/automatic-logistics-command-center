import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { trackingApi } from '@/api/services';
import { FleetGlobe } from '@/components/3d/FleetGlobe';
import { PageTransition } from '@/components/ui/PageTransition';
import { useWebSocket } from '@/hooks/useWebSocket';
import type { Telemetry } from '@/types';
import { Radio, Navigation } from 'lucide-react';

export function TrackingPage() {
  const { data: telemetry = [], refetch } = useQuery({
    queryKey: ['tracking-live'],
    queryFn: () => trackingApi.live().then((r) => r.data),
    refetchInterval: 2000,
  });

  const { messages, connected } = useWebSocket('/ws/telemetry');

  const merged: Telemetry[] = [...telemetry];
  messages.filter((m) => m.channel?.includes('telemetry')).forEach((m) => {
    const t = m.data as Telemetry;
    const idx = merged.findIndex((x) => x.vehicle_id === t.vehicle_id);
    if (idx >= 0) merged[idx] = t;
    else merged.push(t);
  });

  return (
    <PageTransition className="p-6 space-y-6 h-full">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold">Live Tracking</h1>
          <p className="text-gray-500 text-sm flex items-center gap-2">
            <Radio className={`w-4 h-4 ${connected ? 'text-green-400 animate-pulse' : 'text-red-400'}`} />
            WebSocket {connected ? 'connected' : 'disconnected'} · {merged.length} vehicles
          </p>
        </div>
        <button onClick={() => refetch()} className="btn-ghost text-sm">Refresh</button>
      </div>

      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-panel glow-border h-[500px] relative overflow-hidden"
      >
        <FleetGlobe telemetry={merged} className="h-full" />
        <div className="absolute top-4 right-4 glass-panel px-3 py-2 text-xs">
          <div className="flex items-center gap-2 text-green-400"><span className="w-2 h-2 rounded-full bg-green-400" /> En Route</div>
          <div className="flex items-center gap-2 text-blue-400 mt-1"><span className="w-2 h-2 rounded-full bg-blue-400" /> Idle</div>
          <div className="flex items-center gap-2 text-red-400 mt-1"><span className="w-2 h-2 rounded-full bg-red-400" /> Incident</div>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 max-h-64 overflow-y-auto">
        {merged.slice(0, 40).map((t, i) => (
          <motion.div
            key={t.vehicle_id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.02 }}
            className="glass-panel p-3 text-xs font-mono"
          >
            <div className="flex items-center gap-2 mb-2">
              <Navigation className="w-3 h-3 text-blue-400" />
              <span className="text-blue-400 truncate">{t.vehicle_id.slice(0, 10)}</span>
            </div>
            <p className="text-gray-400">{t.latitude.toFixed(4)}° / {t.longitude.toFixed(4)}°</p>
            <p className="text-green-400 mt-1">{t.speed_kmh.toFixed(1)} km/h · {t.fuel_level.toFixed(0)}% fuel</p>
          </motion.div>
        ))}
      </div>
    </PageTransition>
  );
}
