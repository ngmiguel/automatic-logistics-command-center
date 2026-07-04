import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import { analyticsApi } from '@/api/services';
import { PageTransition } from '@/components/ui/PageTransition';
import { StatCard } from '@/components/ui/StatCard';
import { BarChart3, PieChart as PieIcon, TrendingUp, AlertTriangle } from 'lucide-react';

const COLORS = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#6b7280'];

export function AnalyticsPage() {
  const { data: summary } = useQuery({
    queryKey: ['analytics-full'],
    queryFn: () => analyticsApi.summary().then((r) => r.data),
    refetchInterval: 10000,
  });

  const fleet = summary?.fleet;
  const missions = summary?.missions as Record<string, number> | undefined;
  const incidents = summary?.incidents as Record<string, number> | undefined;

  const fleetStateData = fleet ? [
    { name: 'En Route', value: fleet.en_route_vehicles },
    { name: 'Idle', value: fleet.idle_vehicles },
    { name: 'Maintenance', value: fleet.maintenance_vehicles },
    { name: 'Incidents', value: fleet.incident_vehicles },
  ] : [];

  const missionData = missions ? [
    { name: 'Pending', value: missions.pending || 0 },
    { name: 'In Progress', value: missions.in_progress || 0 },
    { name: 'Completed', value: missions.completed || 0 },
    { name: 'Cancelled', value: missions.cancelled || 0 },
  ] : [];

  const trendData = Array.from({ length: 12 }, (_, i) => ({
    hour: `${i * 2}h`,
    utilization: 60 + Math.random() * 30,
    incidents: Math.random() * 5,
  }));

  return (
    <PageTransition className="p-6 space-y-6">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="font-display text-2xl font-bold">Analytics</h1>
        <p className="text-gray-500 text-sm">Fleet performance & operational KPIs</p>
      </motion.div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard title="Utilization" value={fleet ? `${(fleet.fleet_utilization_rate * 100).toFixed(1)}%` : '—'} icon={TrendingUp} color="green" />
        <StatCard title="Completion Rate" value={missions?.completion_rate ? `${(Number(missions.completion_rate) * 100).toFixed(0)}%` : '—'} icon={BarChart3} />
        <StatCard title="Open Incidents" value={incidents?.open_incidents ?? '—'} icon={AlertTriangle} color="red" />
        <StatCard title="Critical" value={incidents?.critical_incidents ?? '—'} icon={PieIcon} color="amber" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass-panel glow-border p-6">
          <h3 className="font-display text-sm text-blue-400 mb-4">FLEET STATE DISTRIBUTION</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={fleetStateData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label>
                {fleetStateData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip contentStyle={{ background: '#111827', border: '1px solid #374151' }} />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="glass-panel glow-border p-6">
          <h3 className="font-display text-sm text-blue-400 mb-4">MISSION STATUS</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={missionData}>
              <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 11 }} />
              <YAxis tick={{ fill: '#9ca3af', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#111827', border: '1px solid #374151' }} />
              <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="glass-panel glow-border p-6 lg:col-span-2">
          <h3 className="font-display text-sm text-blue-400 mb-4">UTILIZATION TREND (24H)</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={trendData}>
              <XAxis dataKey="hour" tick={{ fill: '#9ca3af', fontSize: 11 }} />
              <YAxis tick={{ fill: '#9ca3af', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#111827', border: '1px solid #374151' }} />
              <Line type="monotone" dataKey="utilization" stroke="#3b82f6" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="incidents" stroke="#ef4444" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>
      </div>
    </PageTransition>
  );
}
