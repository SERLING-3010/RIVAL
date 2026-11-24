// Valorar a los compañeros que jugaron (1 a 10). La nota es privada: solo se publica el promedio.

import { useState } from 'react';
import { StyleSheet, Text } from 'react-native';

import type { RatingsController } from '../../controllers/useMatchday';
import { parseScore } from '../../domain/matchdayModels';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { TextField } from '../components/TextField';
import { colors, font } from '../theme';

interface Props {
  controller: RatingsController;
  onBack: () => void;
}

export function RateTeammatesScreen({ controller, onBack }: Props) {
  const [scores, setScores] = useState<Record<number, string>>({});
  const [error, setError] = useState<string | null>(null);
  const send = (userId: number) => {
    const score = parseScore(scores[userId] ?? '');
    if (score === null) return setError('La valoración es un número del 1 al 10.');
    setError(null);
    void controller.handleRate(userId, score);
  };
  return (
    <Screen title="Valorar compañeros" onBack={onBack}>
      <Text style={styles.meta}>
        Tu nota es privada: en la ficha solo se ve el promedio y cuántos votos tiene.
      </Text>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(people) =>
          people.map((p) => (
            <Card key={p.user_id} title={p.display_name}>
              <TextField
                label={`Nota para ${p.display_name} (1 a 10)`}
                keyboardType="number-pad"
                value={scores[p.user_id] ?? ''}
                onChangeText={(v) => setScores((s) => ({ ...s, [p.user_id]: v }))}
              />
              <PrimaryButton
                label="Valorar"
                disabled={controller.action.busy}
                onPress={() => send(p.user_id)}
              />
            </Card>
          ))
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
