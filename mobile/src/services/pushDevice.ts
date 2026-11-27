// Notificaciones del teléfono (Sprint 24): permiso, identificador de Expo y aviso con la app abierta.
// Si algo falla (sin permiso, simulador, Expo Go sin soporte), devuelve null y la app sigue igual.

import Constants from 'expo-constants';
import * as Notifications from 'expo-notifications';

let lastToken: string | null = null;

/** Con la app abierta, el aviso también se muestra arriba (sin sonido extra). */
export function showWhileOpen(): void {
  Notifications.setNotificationHandler({
    handleNotification: async () => ({
      shouldShowBanner: true,
      shouldShowList: true,
      shouldPlaySound: false,
      shouldSetBadge: false,
    }),
  });
}

function projectId(): string | null {
  const extra: unknown = Constants.expoConfig?.extra;
  if (typeof extra !== 'object' || extra === null || !('eas' in extra)) return null;
  const eas: unknown = extra.eas;
  if (typeof eas !== 'object' || eas === null || !('projectId' in eas)) return null;
  return typeof eas.projectId === 'string' ? eas.projectId : null;
}

/** Pide permiso (iOS lo pregunta una sola vez) y devuelve el identificador de avisos, o null. */
export async function pushToken(): Promise<string | null> {
  try {
    const current = await Notifications.getPermissionsAsync();
    const granted = current.granted || (await Notifications.requestPermissionsAsync()).granted;
    const id = projectId();
    if (!granted || id === null) return null;
    lastToken = (await Notifications.getExpoPushTokenAsync({ projectId: id })).data;
    return lastToken;
  } catch {
    return null;
  }
}

/** El último identificador registrado, para quitarlo al cerrar sesión. */
export function registeredToken(): string | null {
  return lastToken;
}

export type NoticeScreen = 'pending' | 'myCard' | 'home';

/** Al tocar un aviso se abre la pantalla que trae (Sprint 26): tu ficha, el inicio o «Pendientes». */
export function onNoticeTapped(open: (screen: NoticeScreen) => void): () => void {
  const subscription = Notifications.addNotificationResponseReceivedListener((response) => {
    const data: unknown = response.notification.request.content.data;
    const screen = typeof data === 'object' && data !== null && 'open' in data ? data.open : null;
    open(screen === 'myCard' || screen === 'home' ? screen : 'pending');
  });
  return () => subscription.remove();
}
