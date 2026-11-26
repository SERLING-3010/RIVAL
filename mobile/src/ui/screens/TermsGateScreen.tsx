// Aceptar Términos y Privacidad (Sprint 27) para cuentas que existían antes o cuando cambia la versión.

import { useState } from 'react';
import { StyleSheet, Text } from 'react-native';

import { toAppError } from '../../domain/appError';
import { TERMS_VERSION } from '../../domain/legalTerms';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { TermsCheck } from '../components/TermsCheck';
import { colors, font } from '../theme';
import { LegalScreen } from './LegalScreen';

interface Props {
  onAccept: (version: string) => Promise<void>;
  onLogout: () => void;
}

export function TermsGateScreen({ onAccept, onLogout }: Props) {
  const [checked, setChecked] = useState(false);
  const [error, setError] = useState<string | undefined>();
  const [reading, setReading] = useState<'terms' | 'privacy' | null>(null);
  const [busy, setBusy] = useState(false);
  if (reading) return <LegalScreen doc={reading} onBack={() => setReading(null)} />;
  const accept = async () => {
    if (!checked) {
      setError('Marca la casilla para continuar.');
      return;
    }
    setBusy(true);
    try {
      await onAccept(TERMS_VERSION);
    } catch (e) {
      setError(toAppError(e).message);
    } finally {
      setBusy(false);
    }
  };
  return (
    <Screen title="Antes de seguir">
      <Text style={styles.body}>
        RIVAL tiene Términos de uso y una Política de privacidad. Léelos y acéptalos para seguir usando la
        app.
      </Text>
      <TermsCheck
        checked={checked}
        error={error}
        onToggle={() => {
          setChecked((c) => !c);
          setError(undefined);
        }}
        onOpen={setReading}
      />
      <PrimaryButton label="Aceptar y seguir" loading={busy} onPress={() => void accept()} />
      <PrimaryButton label="Cerrar sesión" variant="secondary" onPress={onLogout} />
    </Screen>
  );
}

const styles = StyleSheet.create({
  body: { color: colors.text, fontSize: font.body },
});
