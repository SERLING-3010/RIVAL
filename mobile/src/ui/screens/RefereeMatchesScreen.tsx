// Mis partidos como árbitro: aceptar o rechazar, y fijar el resultado después de jugar.

import { useState } from 'react';
import { StyleSheet, Text } from 'react-native';

import type { RefereeMatchesController } from '../../controllers/useSeason';
import { formatLocal } from '../../domain/dateTime';
import { PLACE_LABEL } from '../../domain/matchLabels';
import { canRefereeReport } from '../../domain/seasonModels';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { TextField } from '../components/TextField';
import { colors, font } from '../theme';

interface Props {
  controller: RefereeMatchesController;
  onBack: () => void;
}

const goals = (text: string): number | null => (/^\d{1,3}$/.test(text.trim()) ? Number(text) : null);

export function RefereeMatchesScreen({ controller, onBack }: Props) {
  const [scores, setScores] = useState<Record<number, { host: string; guest: string }>>({});
  const [error, setError] = useState<string | null>(null);
  const busy = controller.action.busy;
  const report = (contractId: number) => {
    const s = scores[contractId] ?? { host: '', guest: '' };
    const h = goals(s.host);
    const g = goals(s.guest);
    if (h === null || g === null)
      return setError('Escribe el marcador de cada equipo con números de 0 a 999.');
    setError(null);
    void controller.handleReport(contractId, h, g);
  };
  const edit = (id: number, side: 'host' | 'guest', v: string) =>
    setScores((all) => ({ ...all, [id]: { ...(all[id] ?? { host: '', guest: '' }), [side]: v } }));
  return (
    <Screen title="Mis partidos como árbitro" onBack={onBack}>
      <Text style={styles.meta}>
        Tu marcador vale por sí solo y resuelve las disputas. El pago se arregla por fuera.
      </Text>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(items) =>
          items.map((m) => (
            <Card
              key={m.assignment_id}
              title={`${m.host_name} vs ${m.guest_name}`}
              subtitle={`${m.league_name} · ${formatLocal(m.kickoff_at)} · ${PLACE_LABEL[m.place_kind]}${m.place_note ? ` · ${m.place_note}` : ''}`}
              badge={
                m.result_status === 'CONFIRMED'
                  ? `${m.host_score} – ${m.guest_score}`
                  : m.status === 'PENDING'
                    ? 'Por aceptar'
                    : 'Aceptado'
              }
            >
              {m.status === 'PENDING' ? (
                <>
                  <PrimaryButton
                    label="Aceptar partido"
                    disabled={busy}
                    onPress={() => void controller.handleRespond(m.assignment_id, true)}
                  />
                  <PrimaryButton
                    label="Rechazar"
                    variant="secondary"
                    disabled={busy}
                    onPress={() => void controller.handleRespond(m.assignment_id, false)}
                  />
                </>
              ) : null}
              {canRefereeReport(m, new Date()) ? (
                <>
                  <TextField
                    label={`Goles de ${m.host_name}`}
                    keyboardType="number-pad"
                    value={scores[m.contract_id]?.host ?? ''}
                    onChangeText={(v) => edit(m.contract_id, 'host', v)}
                  />
                  <TextField
                    label={`Goles de ${m.guest_name}`}
                    keyboardType="number-pad"
                    value={scores[m.contract_id]?.guest ?? ''}
                    onChangeText={(v) => edit(m.contract_id, 'guest', v)}
                  />
                  <PrimaryButton
                    label="Fijar resultado"
                    disabled={busy}
                    onPress={() => report(m.contract_id)}
                  />
                </>
              ) : null}
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
