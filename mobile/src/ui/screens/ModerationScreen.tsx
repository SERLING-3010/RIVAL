// Cola de la persona moderadora: decidir reportes (con motivo) y apelaciones de otros moderadores.

import { useState } from 'react';
import { StyleSheet, Text } from 'react-native';

import type { ModerationController } from '../../controllers/useModeration';
import { formatLocal } from '../../domain/dateTime';
import { CATEGORY_LABEL, textError } from '../../domain/moderationModels';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { TextField } from '../components/TextField';
import { colors, font } from '../theme';

interface Props {
  controller: ModerationController;
  onBack: () => void;
}

export function ModerationScreen({ controller, onBack }: Props) {
  const [notes, setNotes] = useState<Record<number, string>>({});
  const [days, setDays] = useState<Record<number, string>>({});
  const [error, setError] = useState<string | null>(null);
  const busy = controller.action.busy;
  const withNote = (id: number, act: (note: string) => void) => {
    const problem = textError(notes[id] ?? '', 5, 300, 'El motivo');
    setError(problem);
    if (!problem) act((notes[id] ?? '').trim());
  };
  const suspend = (id: number) => {
    const n = Number(days[id] ?? '');
    if (!(n >= 1 && n <= 30)) return setError('La suspensión va de 1 a 30 días.');
    withNote(id, (note) => void controller.handleSanction(id, 'SUSPENSION', n, note));
  };
  return (
    <Screen title="Moderación" onBack={onBack}>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {({ reports, appeals }) => (
          <>
            {reports.map((r) => (
              <Card
                key={`r${r.id}`}
                title={`${CATEGORY_LABEL[r.category]}: ${r.target}`}
                subtitle={formatLocal(r.created_at)}
              >
                <Text style={styles.line}>{r.description}</Text>
                <TextField
                  label="Motivo de la decisión"
                  value={notes[r.id] ?? ''}
                  onChangeText={(v) => setNotes((x) => ({ ...x, [r.id]: v }))}
                />
                <TextField
                  label="Días de suspensión (1 a 30)"
                  keyboardType="number-pad"
                  value={days[r.id] ?? ''}
                  onChangeText={(v) => setDays((x) => ({ ...x, [r.id]: v }))}
                />
                <PrimaryButton
                  label="Descartar"
                  variant="secondary"
                  disabled={busy}
                  onPress={() => withNote(r.id, (n) => void controller.handleDismiss(r.id, n))}
                />
                <PrimaryButton
                  label="Advertir"
                  variant="secondary"
                  disabled={busy}
                  onPress={() =>
                    withNote(r.id, (n) => void controller.handleSanction(r.id, 'WARNING', null, n))
                  }
                />
                <PrimaryButton
                  label="Suspender"
                  variant="danger"
                  disabled={busy}
                  onPress={() => suspend(r.id)}
                />
              </Card>
            ))}
            {appeals.map((a) => (
              <Card
                key={`a${a.id}`}
                title={`Apelación: ${a.kind === 'SUSPENSION' ? 'suspensión' : 'advertencia'}`}
                subtitle={`Motivo original: ${a.reason}`}
              >
                <Text style={styles.line}>“{a.appeal_text}”</Text>
                <PrimaryButton
                  label="Revocar sanción"
                  disabled={busy}
                  onPress={() => void controller.handleAppealDecision(a.id, true)}
                />
                <PrimaryButton
                  label="Confirmar sanción"
                  variant="secondary"
                  disabled={busy}
                  onPress={() => void controller.handleAppealDecision(a.id, false)}
                />
              </Card>
            ))}
          </>
        )}
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
  error: { color: colors.danger, fontSize: font.body },
});
