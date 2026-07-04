import { useEffect, useRef, useState, useCallback } from 'react';
import { getWsUrl } from '@/api/client';
import type { WsMessage } from '@/types';

export function useWebSocket(path: string, enabled = true) {
  const [messages, setMessages] = useState<WsMessage[]>([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    if (!enabled) return;
    const ws = new WebSocket(getWsUrl(path));
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => {
      setConnected(false);
      setTimeout(connect, 3000);
    };
    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data) as WsMessage;
        setMessages((prev) => [msg, ...prev].slice(0, 500));
      } catch { /* ignore */ }
    };
  }, [path, enabled]);

  useEffect(() => {
    connect();
    return () => wsRef.current?.close();
  }, [connect]);

  return { messages, connected };
}
