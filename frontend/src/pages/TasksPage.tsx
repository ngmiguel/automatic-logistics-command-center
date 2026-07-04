import { useMutation } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { tasksApi } from '@/api/services';
import { PageTransition, SlideUp } from '@/components/ui/PageTransition';
import { Zap, Route, Wrench, BarChart3, CheckCircle, Loader2 } from 'lucide-react';
import { useState } from 'react';

const tasks = [
  { id: 'optimize', label: 'Optimize Routes', desc: 'AI-powered route optimization for pending missions', icon: Route, fn: () => tasksApi.optimizeRoutes(), color: 'from-blue-600 to-blue-500' },
  { id: 'maintenance', label: 'Schedule Maintenance', desc: 'Predictive maintenance for low-fuel vehicles', icon: Wrench, fn: () => tasksApi.scheduleMaintenance(), color: 'from-amber-600 to-amber-500' },
  { id: 'analytics', label: 'Compute Analytics', desc: 'Background KPI aggregation via Celery', icon: BarChart3, fn: () => tasksApi.computeAnalytics(), color: 'from-purple-600 to-purple-500' },
];

export function TasksPage() {
  const [results, setResults] = useState<Record<string, { task_id: string; status: string }>>({});

  return (
    <PageTransition className="p-6 space-y-6">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="font-display text-2xl font-bold">Async Tasks</h1>
        <p className="text-gray-500 text-sm">Celery-powered background operations</p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {tasks.map((task, i) => (
          <TaskCard key={task.id} task={task} delay={i * 0.1} onResult={(r) => setResults((prev) => ({ ...prev, [task.id]: r }))} />
        ))}
      </div>

      {Object.entries(results).length > 0 && (
        <SlideUp className="glass-panel glow-border p-6">
          <h3 className="font-display text-sm text-green-400 mb-4">TASK RESULTS</h3>
          <pre className="text-xs font-mono text-gray-400">{JSON.stringify(results, null, 2)}</pre>
        </SlideUp>
      )}
    </PageTransition>
  );
}

function TaskCard({ task, delay, onResult }: {
  task: typeof tasks[0]; delay: number;
  onResult: (r: { task_id: string; status: string }) => void;
}) {
  const mutation = useMutation({
    mutationFn: task.fn,
    onSuccess: (res) => onResult(res.data),
  });

  const Icon = task.icon;

  return (
    <SlideUp delay={delay}>
      <motion.div
        whileHover={{ scale: 1.03, y: -4 }}
        className="glass-panel glow-border p-6 h-full flex flex-col"
      >
        <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${task.color} flex items-center justify-center mb-4`}>
          <Icon className="w-6 h-6" />
        </div>
        <h3 className="font-display font-semibold">{task.label}</h3>
        <p className="text-xs text-gray-500 mt-2 flex-1">{task.desc}</p>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => mutation.mutate()}
          disabled={mutation.isPending}
          className="btn-primary mt-4 w-full flex items-center justify-center gap-2"
        >
          {mutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
          {mutation.isPending ? 'Queuing...' : 'Trigger Task'}
        </motion.button>
        {mutation.isSuccess && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center gap-2 mt-3 text-green-400 text-xs">
            <CheckCircle className="w-4 h-4" /> Task queued
          </motion.div>
        )}
      </motion.div>
    </SlideUp>
  );
}
