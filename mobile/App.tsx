import { StatusBar } from 'expo-status-bar';
import type { ReactNode } from 'react';
import { useEffect } from 'react';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { LoadingScreen, SignedInFlow } from './src/app/SignedInFlow';
import { SignedOutFlow } from './src/app/SignedOutFlow';
import { FeaturesContext } from './src/ui/FeaturesContext';
import { TermsGateScreen } from './src/ui/screens/TermsGateScreen';
import { useLaunchFeatures } from './src/controllers/useLaunchFeatures';
import { useNavigator } from './src/controllers/useNavigator';
import { usePushRegistration } from './src/controllers/usePushRegistration';
import { useSession } from './src/controllers/useSession';

function Root() {
  const session = useSession();
  const navigator = useNavigator({ name: 'rolePicker' });
  const { reset, push } = navigator;
  // Sprints 24 y 26: registra el teléfono; tocar un aviso abre su pantalla (tu ficha, el inicio o Pendientes).
  const me = session.user?.id ?? null;
  usePushRegistration(session.status === 'signedIn' ? session.token : null, (screen) => {
    if (screen === 'myCard' && me !== null) push({ name: 'playerCard', userId: me });
    else if (screen === 'home') reset({ name: 'home' });
    else push({ name: 'pending' });
  });

  // Al entrar o salir de sesión, la pila de navegación vuelve a empezar.
  useEffect(() => {
    if (session.status === 'signedIn') reset({ name: 'home' });
    if (session.status === 'signedOut') reset({ name: 'rolePicker' });
  }, [session.status, reset]);

  if (session.status === 'restoring') {
    return <LoadingScreen />;
  }
  if (session.status === 'signedIn' && session.user?.needs_terms) {
    // Sprint 27: cuentas anteriores o versión nueva de los textos: aceptar antes de seguir.
    return (
      <TermsGateScreen onAccept={session.handleAcceptTerms} onLogout={() => void session.handleLogout()} />
    );
  }
  if (session.status === 'signedIn' && session.user && session.token) {
    return <SignedInFlow session={session} user={session.user} token={session.token} navigator={navigator} />;
  }
  return <SignedOutFlow session={session} navigator={navigator} />;
}

/** Sprint 29: lo que está prendido en este lanzamiento (solo fútbol, sin árbitros ni canchas). */
function LaunchFeatures({ children }: { children: ReactNode }) {
  return <FeaturesContext.Provider value={useLaunchFeatures()}>{children}</FeaturesContext.Provider>;
}

export default function App() {
  return (
    <SafeAreaProvider>
      <StatusBar style="dark" />
      <LaunchFeatures>
        <Root />
      </LaunchFeatures>
    </SafeAreaProvider>
  );
}
