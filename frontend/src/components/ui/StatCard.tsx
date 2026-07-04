import { motion } from 'framer-motion';
import type { ComponentType, SVGProps } from 'react';

interface Props {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: ComponentType<SVGProps<SVGSVGElement>>;
  color?: string;
  delay?: number;
}

export function StatCard({ title, value, subtitle, icon: Icon, color = 'blue', delay = 0 }: Props) {
  const colors: Record<string, string> = {
    blue: 'from-blue-500/20 to-blue-600/5 border-blue-500/30',
    green: 'from-green-500/20 to-green-600/5 border-green-500/30',
    red: 'from-red-500/20 to-red-600/5 border-red-500/30',
    amber: 'from-amber-500/20 to-amber-600/5 border-amber-500/30',
    purple: 'from-purple-500/20 to-purple-600/5 border-purple-500/30',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ delay, duration: 0.5, type: 'spring' }}
      whileHover={{ scale: 1.03, y: -4 }}
      className={`stat-card bg-gradient-to-br ${colors[color]}`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs uppercase tracking-widest text-gray-500 font-medium">{title}</p>
          <motion.p
            key={String(value)}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-3xl font-display font-bold mt-2 text-white"
          >
            {value}
          </motion.p>
          {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
        </div>
        <div className="p-2 rounded-lg bg-white/5">
          <Icon className="w-5 h-5 text-blue-400" />
        </div>
      </div>
    </motion.div>
  );
}
