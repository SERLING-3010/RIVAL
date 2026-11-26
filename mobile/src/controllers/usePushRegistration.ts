// Avisos push (Sprints 24 y 26): al iniciar sesión se registra el teléfono; tocar un aviso abre su pantalla.
// Los avisos son breves y sin datos (decisión del dueño): el detalle se ve dentro de la app.

import { useEffect, useRef } from 'react';

import { pushApi } from '../services/pushApi';
import type { NoticeScreen } from '../services/pushDevice';
import { onNoticeTapped, pushToken, showWhileOpen } from '../services/pushDevice';

export function usePushRegistration(
  sessionToken: string | null,
  openScreen: (screen: NoticeScreen) => void,
): void {
  const open = useRef(openScreen);
  open.current = openScreen;

  useEffect(() => {
    showWhileOpen();
    return onNoticeTapped((screen) => open.current(screen));
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
