// Goles con tipo del partido (Sprint 23): cada equipo ve los suyos y el rival los confirma o rechaza.

import { StyleSheet, Text, View } from 'react-native';

import type { GoalClaimsController } from '../../controllers/useGoalClaims';
import { CLAIM_STATUS_LABEL, GOAL_KIND_LABEL } from '../../domain/goalKinds';
import { colors, font, space } from '../theme';
import { Card } from './Card';
import { PrimaryButton } from './PrimaryButton';

export function GoalClaimsPanel({ controller }: { controller: GoalClaimsController }) {
  if (controller.state.kind !== 'success') return null; // sin goles con tipo, no se muestra nada
  const claims = controller.state.data;
  const busy = controller.action.busy;
  return (
    <Card title="Goles especiales">
      <Text style={styles.meta}>
        Si lo rechazas, sigue contando como gol normal. Sin respuesta en 72 horas, el tipo no cuenta.
      </Text>
      {claims.map((c) => (
        <View key={c.id} style={styles.item}>
          <Text style={styles.line}>
            <Text style={styles.strong}>{c.display_name}</Text> · {GOAL_KIND_LABEL[c.kind]}
          </Text>
          <Text style={styles.meta}>{CLAIM_STATUS_LABEL[c.status]}</Text>
          {c.can_decide ? (
            <View style={styles.row}>
              <View style={styles.cell}>
                <PrimaryButton
                  label="No fue así"
                  variant="secondary"
                  disabled={busy}
                  onPress={() => void controller.handleDecide(c.id, false)}
                />
              </View>
              <View style={styles.cell}>
                <PrimaryButton
                  label="Confirmar"
                  disabled={busy}
                  onPress={() => void controller.handleDecide(c.id, true)}
                />
              </View>
            </View>
          ) : null}
        </View>
      ))}
      {controller.action.message ? (
        <Text style={styles.line} accessibilityLiveRegion="polite">
          {controller.action.message}
        </Text>
      ) : null}
    </Card>
  );
}

const styles = StyleSheet.create({
  item: { gap: space.xs, paddingVertical: space.xs },
  row: { flexDirection: 'row', gap: space.sm },
  cell: { flex: 1 },
  line: { color: colors.text, fontSize: font.body },
  strong: { fontWeight: '700' },
  meta: { color: colors.textMuted, fontSize: font.small },
});
