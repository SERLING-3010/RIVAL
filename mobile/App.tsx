import { StatusBar } from 'expo-status-bar';
import { useEffect } from 'react';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { LoadingScreen, SignedInFlow } from './src/app/SignedInFlow';
import { SignedOutFlow } from './src/app/SignedOutFlow';
import { useNavigator } from './src/controllers/useNavigator';
import { useSession } from './src/controllers/useSession';

function Root() {
  const session = useSession();
  const navigator = useNavigator({ name: 'rolePicker' });
  const { reset } = navigator;

  // Al entrar o salir de sesión, la pila de navegación vuelve a empezar.
  useEffect(() => {
    if (session.status === 'signedIn') reset({ name: 'home' });
    if (session.status === 'signedOut') reset({ name: 'rolePicker' });
  }, [session.status, reset]);

  if (session.status === 'restoring') {
    return <LoadingScreen />;
  }
  if (session.status === 'signedIn' && session.user && session.token) {
    return <SignedInFlow session={session} user={session.user} token={session.token} navigator={navigator} />;
  }
  return <SignedOutFlow session={session} navigator={navigator} />;
}

export default function App() {
  return (
    <SafeAreaProvider>
      <StatusBar style="dark" />
      <Root />
    </SafeAreaProvider>
  );
}
