import { useState, useRef, useEffect } from "react";
import { showToast, removeToast } from '../components/ToastBus';

const WS_PORT = import.meta.env.BACK_PORT || 5000;
const RECONNECT_DELAY = 2000;


const useWebSocket = (onMessage: (event: MessageEvent) => void, debug: boolean = false) => {

  const reconnectId = useRef<number | null>(null);
  const reconnectTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttempts = useRef<number>(0);
  const wsRef = useRef<WebSocket | null>(null);

  const onMessageRef = useRef(onMessage);
  useEffect(() => {
    onMessageRef.current = onMessage;
  }, [onMessage]);

  const wsConnect = (): void => {
    try {
      wsRef.current = new WebSocket(`ws://localhost:${WS_PORT}/ws/prompt`);

      wsRef.current.onopen = () => {
        if (reconnectId.current) {
          removeToast(reconnectId.current);
          showToast("✅ Connected", 3000);
          reconnectId.current = null;
        }
        reconnectAttempts.current = 0;
        if (reconnectTimeout.current) {
          clearTimeout(reconnectTimeout.current);
          reconnectTimeout.current = null;
        }
        if (debug) console.log("WebSocket connection established");
      };

      wsRef.current.onmessage = (event) => {
        onMessageRef.current(event);
      };

      wsRef.current.onclose = () => {
        if (debug) console.log("WebSocket connection closed.");

        if (reconnectAttempts.current < 5) {
          reconnectAttempts.current++;
          if (debug) console.log(`Attempting to reconnect (${reconnectAttempts.current})...`);
          if (reconnectId.current) {
            removeToast(reconnectId.current);
          }
          reconnectId.current = showToast("🔄 Reconnecting...", 50000);
          reconnectTimeout.current = setTimeout(() => {
            wsConnect();
          }, RECONNECT_DELAY);
        }
      };
    } catch (error) {
      console.error('Connection failed:', error);
    }
  };

  const handleSendMessage = (message: string): void => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(message);
    }
    else {
      console.warn("WebSocket is not open. Cannot send message.");
      console.warn("wsRef.current:", wsRef.current);
      console.warn("Current readyState:", wsRef.current?.readyState);
    }
  }

  useEffect(() => {
    wsConnect();

    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
        reconnectTimeout.current = null;
      }

      if (wsRef.current && wsRef.current.readyState !== WebSocket.CLOSED) {
        wsRef.current.close();
        wsRef.current = null;
        if (debug) console.log("WebSocket connection closed");
      }
    };
  }, []);

  return [handleSendMessage] as const;
};

export default useWebSocket;