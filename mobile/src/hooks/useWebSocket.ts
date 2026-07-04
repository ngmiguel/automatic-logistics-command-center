import { useEffect, useRef, useState, useCallback } from 'react';
import { getWsUrl } from '@/api/client';
import type { WsMessage } from '@/types';

export function useWebSocket(path: string, enabled = true) {
  const [lastMessage, setLastMessage] = useState<WsMessage | null>(null);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    if (!enabled) return;
    const url = getWsUrl(path);
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => {
      setConnected(false);
      setTimeout(connect, 3000);
    };
    ws.onerror = () => ws.close();
    ws.onmessage = (ev) => {
      try {
        setLastMessage(JSON.parse(ev.data) as WsMessage);
      } catch {
        /* ignore malformed */
      }
    };
  }, [path, enabled]);

  useEffect(() => {
    connect();
    return () => wsRef.current?.close();
  }, [connect]);

  return { lastMessage, connected };
}
