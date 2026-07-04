import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { useWebSocket } from '@/hooks/useWebSocket';

export function AppLayout() {
  const { connected } = useWebSocket('/ws/dashboard');

  return (
    <div className="flex min-h-screen bg-alcc-bg">
      <Sidebar connected={connected} />
      <main className="flex-1 overflow-auto">
        <Outlet context={{ connected }} />
      </main>
    </div>
  );
}
