import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { routingApi, fleetApi } from '@/api/services';
import { PageTransition } from '@/components/ui/PageTransition';
import { Route, Plus, CheckCircle, Play } from 'lucide-react';

const statusColors: Record<string, string> = {
  pending: 'border-gray-500 text-gray-400',
  assigned: 'border-blue-500 text-blue-400',
  in_progress: 'border-green-500 text-green-400',
  completed: 'border-emerald-500 text-emerald-400',
  cancelled: 'border-red-500 text-red-400',
};

export function MissionsPage() {
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    origin_lat: 48.85, origin_lng: 2.35, dest_lat: 51.5, dest_lng: -0.12,
    cargo_description: '', priority: 1,
  });

  const { data: missions = [] } = useQuery({
    queryKey: ['missions'],
    queryFn: () => routingApi.listMissions().then((r) => r.data),
    refetchInterval: 5000,
  });

  const { data: idleVehicles = [] } = useQuery({
    queryKey: ['idle-vehicles'],
    queryFn: () => fleetApi.listVehicles({ state: 'idle', limit: 20 }).then((r) => r.data),
  });

  const createMission = useMutation({
    mutationFn: () => routingApi.createMission(form),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['missions'] }); setShowForm(false); },
  });

  const assignMission = useMutation({
    mutationFn: ({ mid, vid }: { mid: string; vid: string }) => routingApi.assignMission(mid, vid),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['missions'] }),
  });

  const completeMission = useMutation({
    mutationFn: (id: string) => routingApi.completeMission(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['missions'] }),
  });

  return (
    <PageTransition className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold">Mission Dispatch</h1>
          <p className="text-gray-500 text-sm">{missions.length} missions in system</p>
        </div>
        <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} onClick={() => setShowForm(!showForm)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> New Mission
        </motion.button>
      </div>

      <AnimatePresence>
        {showForm && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} className="glass-panel glow-border p-6 space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {(['origin_lat', 'origin_lng', 'dest_lat', 'dest_lng'] as const).map((k) => (
                <div key={k}>
                  <label className="text-xs text-gray-500">{k.replace('_', ' ')}</label>
                  <input type="number" step="0.01" value={form[k]} onChange={(e) => setForm({ ...form, [k]: +e.target.value })} className="input-field mt-1" />
                </div>
              ))}
            </div>
            <input placeholder="Cargo description" value={form.cargo_description} onChange={(e) => setForm({ ...form, cargo_description: e.target.value })} className="input-field" />
            <button onClick={() => createMission.mutate()} className="btn-primary">Create Mission</button>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="space-y-3">
        {missions.map((m, i) => (
          <motion.div
            key={m.id}
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.04 }}
            className="glass-panel p-5 glow-border"
          >
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-4">
                <Route className="w-5 h-5 text-blue-400" />
                <div>
                  <p className="font-mono text-sm">{m.id.slice(0, 8)}...</p>
                  <p className="text-xs text-gray-500 mt-1">
                    ({m.origin_lat.toFixed(2)}, {m.origin_lng.toFixed(2)}) → ({m.dest_lat.toFixed(2)}, {m.dest_lng.toFixed(2)})
                  </p>
                  <p className="text-xs text-gray-400">{m.estimated_distance_km.toFixed(0)} km · {m.cargo_description || 'No cargo'}</p>
                </div>
              </div>
              <span className={`text-xs px-3 py-1 rounded-full border ${statusColors[m.status]}`}>{m.status}</span>
              <div className="flex gap-2">
                {m.status === 'pending' && idleVehicles[0] && (
                  <button onClick={() => assignMission.mutate({ mid: m.id, vid: idleVehicles[0].id })} className="btn-ghost text-xs flex items-center gap-1">
                    <Play className="w-3 h-3" /> Assign
                  </button>
                )}
                {m.status === 'in_progress' && (
                  <button onClick={() => completeMission.mutate(m.id)} className="btn-ghost text-xs flex items-center gap-1 text-green-400">
                    <CheckCircle className="w-3 h-3" /> Complete
                  </button>
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </PageTransition>
  );
}
