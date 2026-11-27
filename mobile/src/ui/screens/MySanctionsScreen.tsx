// Mis sanciones: motivo, hasta cuándo y apelación (una vez, dentro de 14 días).

import { useState } from 'react';
import { StyleSheet, Text } from 'react-native';

import type { MySanctionsController } from '../../controllers/useModeration';
import { formatLocal } from '../../domain/dateTime';
import { canAppeal, textError } from '../../domain/moderationModels';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { TextField } from '../components/TextField';
import { colors, font } from '../theme';

interface Props {
  controller: MySanctionsController;
  onBack: () => void;
}

const OUTCOME = { UPHELD: 'Apelación rechazada', REVOKED: 'Sanción revocada' } as const;

export function MySanctionsScreen({ controller, onBack }: Props) {
  const [texts, setTexts] = useState<Record<number, string>>({});
  const [error, setError] = useState<string | null>(null);
  const now = new Date();
  const send = (id: number) => {
    const text = texts[id] ?? '';
    const problem = textError(text, 10, 500, 'La apelación');
    setError(problem);
    if (!problem) void controller.handleAppeal(id, text.trim());
  };
  return (
    <Screen title="Mis sanciones" onBack={onBack}>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(me) =>
          me.sanctions.length === 0 ? (
            <Text style={styles.meta}>No tienes sanciones.</Text>
          ) : (
            me.sanctions.map((s) => (
              <Card
                key={s.id}
                title={s.kind === 'SUSPENSION' ? 'Suspensión' : 'Advertencia'}
                subtitle={s.ends_at ? `Hasta ${formatLocal(s.ends_at)}` : formatLocal(s.created_at)}
                badge={
                  s.appeal_outcome
                    ? OUTCOME[s.appeal_outcome]
                    : s.appeal_text
                      ? 'Apelación en revisión'
                      : undefined
                }
              >
                <Text style={styles.line}>Motivo: {s.reason}</Text>
                {canAppeal(s, now) ? (
                  <>
                    <TextField
                      label="Tu apelación (10 a 500 caracteres)"
                      value={texts[s.id] ?? ''}
                      onChangeText={(v) => setTexts((t) => ({ ...t, [s.id]: v }))}
                    />
                    <PrimaryButton
                      label="Apelar"
                      disabled={controller.action.busy}
                      onPress={() => send(s.id)}
                    />
                  </>
                ) : null}
              </Card>
            ))
          )
        }
      </StateView>
      {error ? <Text style={styles.error}>{error}</Text> : null}
      {controller.action.message ? (
        <Text style={styles.line} accessibilityLiveRegion="polite">
          {controller.action.message}
        </Text>
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  line: { color: colors.text, fontSize: font.small },
  meta: { color: colors.textMuted, fontSize: font.small },
  error: { color: colors.danger, fontSize: font.body },
});
