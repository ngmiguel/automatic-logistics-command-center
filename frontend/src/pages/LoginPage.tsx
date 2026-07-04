import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ShowroomScene, SHOWROOM_VEHICLES } from '@/components/3d/ShowroomScene';
import { authApi } from '@/api/services';
import { useAuthStore } from '@/store/authStore';
import { LogIn, Shield } from 'lucide-react';

const DEMO_ACCOUNTS = [
  { email: 'admin@alcc.io', password: 'admin1234', role: 'Admin' },
  { email: 'dispatcher@alcc.io', password: 'dispatch123', role: 'Dispatcher' },
  { email: 'operator@alcc.io', password: 'operator123', role: 'Operator' },
];

export function LoginPage() {
  const [email, setEmail] = useState('operator@alcc.io');
  const [password, setPassword] = useState('operator123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const setAuth = useAuthStore((s) => s.setAuth);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const { data: tokenData } = await authApi.login(email, password);
      useAuthStore.setState({ token: tokenData.access_token });
      const { data: user } = await authApi.me();
      setAuth(tokenData.access_token, user);
      navigate('/dashboard');
    } catch {
      setError('Invalid credentials. Start the backend or use demo accounts.');
    } finally {
      setLoading(false);
    }
  };

  const quickLogin = (acc: typeof DEMO_ACCOUNTS[0]) => {
    setEmail(acc.email);
    setPassword(acc.password);
  };

  return (
    <div className="min-h-screen flex bg-alcc-bg overflow-hidden">
      <div className="hidden lg:block lg:w-3/5 relative">
        <ShowroomScene className="absolute inset-0" />
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-alcc-bg/30 to-alcc-bg pointer-events-none" />
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="absolute bottom-8 left-8 right-8"
        >
          <div className="flex gap-4">
            {SHOWROOM_VEHICLES.map((v, i) => (
              <motion.div
                key={v.variant}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.8 + i * 0.15 }}
                className="glass-panel px-4 py-3 flex-1"
              >
                <p className="text-xs text-blue-400 font-display">{v.label}</p>
                <p className="text-[10px] text-gray-500 mt-1">Autonomous Fleet Class</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>

      <div className="flex-1 flex items-center justify-center p-8">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full max-w-md"
        >
          <div className="text-center mb-8">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
              className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center"
            >
              <Shield className="w-8 h-8" />
            </motion.div>
            <h1 className="font-display text-3xl font-bold tracking-wider">ALCC</h1>
            <p className="text-gray-500 mt-2 text-sm">Autonomous Logistics Command Center</p>
          </div>

          <form onSubmit={handleLogin} className="glass-panel p-8 space-y-5 glow-border">
            <div>
              <label className="text-xs text-gray-400 uppercase tracking-wider">Email</label>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="input-field mt-2" />
            </div>
            <div>
              <label className="text-xs text-gray-400 uppercase tracking-wider">Password</label>
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="input-field mt-2" />
            </div>
            {error && <p className="text-red-400 text-sm">{error}</p>}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={loading}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              <LogIn className="w-5 h-5" />
              {loading ? 'Connecting...' : 'Enter Command Center'}
            </motion.button>
          </form>

          <div className="mt-6 space-y-2">
            <p className="text-xs text-gray-500 text-center">Quick access — demo accounts</p>
            <div className="flex gap-2 flex-wrap justify-center">
              {DEMO_ACCOUNTS.map((acc) => (
                <button key={acc.email} onClick={() => quickLogin(acc)} className="btn-ghost text-xs">
                  {acc.role}
                </button>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
