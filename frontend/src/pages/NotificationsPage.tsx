import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { notificationApi } from '@/api/services';
import { PageTransition } from '@/components/ui/PageTransition';
import { Bell, AlertTriangle, CheckCircle, Fuel, Wrench } from 'lucide-react';

const severityStyles: Record<string, string> = {
  low: 'border-gray-500/50',
  medium: 'border-amber-500/50 bg-amber-500/5',
  high: 'border-orange-500/50 bg-orange-500/5',
  critical: 'border-red-500/50 bg-red-500/10 animate-pulse',
};

const typeIcons: Record<string, typeof Bell> = {
  incident: AlertTriangle,
  low_fuel: Fuel,
  maintenance: Wrench,
  system: Bell,
};

export function NotificationsPage() {
  const qc = useQueryClient();

  const { data: notifications = [] } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => notificationApi.list().then((r) => r.data),
    refetchInterval: 5000,
  });

  const { data: incidents = [] } = useQuery({
    queryKey: ['incidents'],
    queryFn: () => notificationApi.listIncidents().then((r) => r.data),
    refetchInterval: 5000,
  });

  const resolve = useMutation({
    mutationFn: (id: string) => notificationApi.resolveIncident(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['incidents'] }),
  });

  return (
    <PageTransition className="p-6 space-y-6">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="font-display text-2xl font-bold">Alerts & Incidents</h1>
        <p className="text-gray-500 text-sm">{notifications.length} unread · {incidents.length} open incidents</p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h2 className="font-display text-sm text-blue-400 tracking-wider mb-4">NOTIFICATIONS</h2>
          <div className="space-y-3">
            {notifications.map((n, i) => {
              const Icon = typeIcons[n.type] || Bell;
              return (
                <motion.div
                  key={n.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className={`glass-panel p-4 border-l-4 ${severityStyles[n.severity]}`}
                >
                  <div className="flex items-start gap-3">
                    <Icon className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
                    <div>
                      <p className="font-medium text-sm">{n.title}</p>
                      <p className="text-xs text-gray-500 mt-1">{n.message}</p>
                      <span className="text-[10px] text-gray-600 uppercase mt-2 inline-block">{n.severity}</span>
                    </div>
                  </div>
                </motion.div>
              );
            })}
            {!notifications.length && <p className="text-gray-500 text-sm">No unread notifications</p>}
          </div>
        </div>

        <div>
          <h2 className="font-display text-sm text-red-400 tracking-wider mb-4">OPEN INCIDENTS</h2>
          <div className="space-y-3">
            {incidents.map((inc, i) => (
              <motion.div
                key={inc.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                className={`glass-panel p-4 glow-border ${inc.severity === 'critical' ? 'animate-pulse' : ''}`}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-sm font-medium text-red-400">{inc.severity.toUpperCase()}</p>
                    <p className="text-xs text-gray-400 mt-1">{inc.description}</p>
                    <p className="text-[10px] text-gray-600 font-mono mt-2">Vehicle: {inc.vehicle_id.slice(0, 8)}</p>
                  </div>
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => resolve.mutate(inc.id)}
                    className="btn-ghost text-green-400 p-2"
                  >
                    <CheckCircle className="w-5 h-5" />
                  </motion.button>
                </div>
              </motion.div>
            ))}
            {!incidents.length && <p className="text-gray-500 text-sm">No open incidents</p>}
          </div>
        </div>
      </div>
    </PageTransition>
  );
}
