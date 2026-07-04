import { NavLink, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  LayoutDashboard, Truck, Route, MapPin, Bell, BarChart3, Zap, LogOut, Radio,
} from 'lucide-react';
import { useAuthStore } from '@/store/authStore';

const links = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Command Center' },
  { to: '/fleet', icon: Truck, label: 'Fleet' },
  { to: '/missions', icon: Route, label: 'Missions' },
  { to: '/tracking', icon: MapPin, label: 'Live Tracking' },
  { to: '/notifications', icon: Bell, label: 'Alerts' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  { to: '/tasks', icon: Zap, label: 'Async Tasks' },
];

export function Sidebar({ connected }: { connected?: boolean }) {
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);

  return (
    <motion.aside
      initial={{ x: -80, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="w-64 min-h-screen glass-panel border-r border-alcc-border flex flex-col p-4"
    >
      <div className="mb-8 px-2">
        <h1 className="font-display font-bold text-lg tracking-wider text-blue-400">ALCC</h1>
        <p className="text-[10px] text-gray-500 uppercase tracking-[0.2em] mt-1">Command Center</p>
      </div>

      <nav className="flex-1 space-y-1">
        {links.map(({ to, icon: Icon, label }, i) => (
          <motion.div key={to} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }}>
            <NavLink
              to={to}
              className={({ isActive }) => (isActive ? 'nav-link-active' : 'nav-link')}
            >
              <Icon className="w-5 h-5" />
              <span className="text-sm font-medium">{label}</span>
            </NavLink>
          </motion.div>
        ))}
      </nav>

      <div className="mt-auto pt-4 border-t border-alcc-border space-y-3">
        {connected !== undefined && (
          <div className="flex items-center gap-2 px-4 text-xs">
            <Radio className={`w-3 h-3 ${connected ? 'text-green-400 animate-pulse' : 'text-red-400'}`} />
            <span className={connected ? 'text-green-400' : 'text-red-400'}>
              {connected ? 'Live Feed' : 'Reconnecting...'}
            </span>
          </div>
        )}
        <p className="px-4 text-xs text-gray-500 truncate">{user?.email}</p>
        <button
          onClick={() => { logout(); navigate('/login'); }}
          className="nav-link w-full text-red-400 hover:text-red-300"
        >
          <LogOut className="w-5 h-5" />
          <span>Logout</span>
        </button>
      </div>
    </motion.aside>
  );
}
