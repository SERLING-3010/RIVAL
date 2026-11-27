// Copa eliminatoria de la liga: cuadro por rondas; el organizador la arma y define los penales.

import { useState } from 'react';
import { StyleSheet, Text } from 'react-native';

import type { CupController } from '../../controllers/useCup';
import type { CupMatch } from '../../domain/cupModels';
import { matchLine } from '../../domain/cupModels';
import { formatLocal } from '../../domain/dateTime';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { TextField } from '../components/TextField';
import { colors, font } from '../theme';

interface Props {
  controller: CupController;
  canManage: boolean;
  onOpenContract: (contractId: number) => void;
  onBack: () => void;
}

export function CupScreen({ controller, canManage, onOpenContract, onBack }: Props) {
  const [first, setFirst] = useState('');
  const [days, setDays] = useState('7');
  const [error, setError] = useState<string | null>(null);
  const busy = controller.action.busy;
  const penalties = (m: CupMatch) =>
    [
      [m.host_team_id, m.host_name],
      [m.guest_team_id, m.guest_name],
    ].map(([id, name]) =>
      typeof id === 'number' ? (
        <PrimaryButton
          key={id}
          label={`Ganó por penales: ${name ?? ''}`}
          variant="secondary"
          disabled={busy}
          onPress={() => void controller.handleTiebreak(m.id, id)}
        />
      ) : null,
    );
  return (
    <Screen title="Copa" onBack={onBack}>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(cup) => (
          <>
            {cup.champion_name ? <Text style={styles.title}>Campeón: {cup.champion_name}</Text> : null}
            {cup.rounds.map((r) => (
              <Card key={r.number} title={r.name} subtitle={`Fecha prevista: ${formatLocal(r.planned_at)}`}>
                {r.matches.map((m) => (
                  <Card
                    key={m.id}
                    title={matchLine(m, r.number === 1)}
                    badge={m.winner_name ? `Pasa ${m.winner_name}` : m.needs_tiebreak ? 'Empate' : undefined}
                    onPress={m.contract_id !== null ? () => onOpenContract(m.contract_id ?? 0) : undefined}
                  >
                    {m.needs_tiebreak && cup.can_manage ? penalties(m) : null}
                  </Card>
                ))}
              </Card>
            ))}
          </>
        )}
      </StateView>
      {canManage && controller.state.kind === 'error' ? ( // sin copa todavía (no si falta conexión)
        <Card
          title="Armar la copa"
          subtitle="Con los equipos aprobados, sembrados por nivel. Una copa por liga."
        >
          <TextField label="Primera ronda (dd/mm/aaaa hh:mm)" value={first} onChangeText={setFirst} />
          <TextField
            label="Días entre rondas"
            keyboardType="number-pad"
            value={days}
            onChangeText={setDays}
          />
          <PrimaryButton
            label="Armar copa"
            disabled={busy}
            onPress={() => void controller.handleCreate(first, days).then(setError)}
          />
          {error ? <Text style={styles.error}>{error}</Text> : null}
        </Card>
      ) : null}
      {controller.action.message ? (
        <Text style={styles.line} accessibilityLiveRegion="polite">
          {controller.action.message}
        </Text>
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  title: { color: colors.text, fontSize: font.heading, fontWeight: '700' },
  line: { color: colors.text, fontSize: font.small },
  error: { color: colors.danger, fontSize: font.body },
});
