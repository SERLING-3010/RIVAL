// Composición sin sesión: elegir rol → registro, o iniciar sesión.

import { useCatalog } from '../controllers/useCatalog';
import { useLoginForm } from '../controllers/useLoginForm';
import type { Navigator } from '../controllers/useNavigator';
import { useRegistrationForm } from '../controllers/useRegistrationForm';
import type { Session } from '../controllers/useSession';
import type { UserRole } from '../domain/models';
import { LegalScreen } from '../ui/screens/LegalScreen';
import { LoginScreen } from '../ui/screens/LoginScreen';
import { RegisterScreen } from '../ui/screens/RegisterScreen';
import { RolePickerScreen } from '../ui/screens/RolePickerScreen';

interface Props {
  session: Session;
  navigator: Navigator;
}

function RegisterContainer({
  role,
  session,
  onBack,
  onOpenLegal,
}: {
  role: UserRole;
  session: Session;
  onBack: () => void;
  onOpenLegal: (doc: 'terms' | 'privacy') => void;
}) {
  const controller = useRegistrationForm(role, session.handleRegister);
  const catalog = useCatalog();
  return (
    <RegisterScreen
      controller={controller}
      catalog={catalog.state}
      onRetryCatalog={catalog.handleRetry}
      onBack={onBack}
      onOpenLegal={onOpenLegal}
    />
  );
}

function LoginContainer({ session, onBack }: { session: Session; onBack: () => void }) {
  return <LoginScreen controller={useLoginForm(session.handleLogin)} onBack={onBack} />;
}

export function SignedOutFlow({ session, navigator }: Props) {
  const route = navigator.current;
  if (route.name === 'register') {
    return (
      <RegisterContainer
        role={route.role}
        session={session}
        onBack={navigator.goBack}
        onOpenLegal={(doc) => navigator.push({ name: 'legal', doc })}
      />
    );
  }
  if (route.name === 'legal') {
    return <LegalScreen doc={route.doc} onBack={navigator.goBack} />;
  }
  if (route.name === 'login') {
    return <LoginContainer session={session} onBack={navigator.goBack} />;
  }
  return (
    <RolePickerScreen
      onPickRole={(role) => navigator.push({ name: 'register', role })}
      onLogin={() => navigator.push({ name: 'login' })}
    />
  );
}
