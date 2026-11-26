// Avisos push (Sprint 24): al iniciar sesión se registra el teléfono; tocar un aviso abre «Pendientes».
// Los avisos son breves y sin datos (decisión del dueño): el detalle se ve dentro de la app.

import { useEffect, useRef } from 'react';

import { pushApi } from '../services/pushApi';
import { onNoticeTapped, pushToken, showWhileOpen } from '../services/pushDevice';

export function usePushRegistration(sessionToken: string | null, openPending: () => void): void {
  const open = useRef(openPending);
  open.current = openPending;

  useEffect(() => {
    showWhileOpen();
    return onNoticeTapped(() => open.current());
  }, []);

  useEffect(() => {
    if (sessionToken === null) return undefined;
    let alive = true;
    void pushToken().then(async (deviceToken) => {
      if (!alive || deviceToken === null) return;
      await pushApi.register(sessionToken, deviceToken).catch(() => undefined); // sin red: se intenta al volver
    });
    return () => {
      alive = false;
    };
  }, [sessionToken]);
}
