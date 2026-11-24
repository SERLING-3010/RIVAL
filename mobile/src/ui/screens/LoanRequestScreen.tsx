// Pedir un jugador prestado para este partido: elegir equipo, luego jugador. Decide su DT y él.

import { StyleSheet, Text } from 'react-native';

import type { LoanRequestController } from '../../controllers/useLoans';
import { borrowable, LOAN_STATUS_LABEL } from '../../domain/loanModels';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { colors, font } from '../theme';

interface Props {
  controller: LoanRequestController;
  onBack: () => void;
}

export function LoanRequestScreen({ controller, onBack }: Props) {
  const { current, teams, squad, action } = controller;
  const taken = current.state.kind === 'success' ? current.state.data.map((l) => l.player_id) : [];
  return (
    <Screen title="Pedir jugador prestado" onBack={onBack}>
      <Text style={styles.meta}>
        Solo para este partido. Primero acepta el DT de su equipo y después el jugador.
      </Text>
      <StateView state={current.state} onRetry={current.handleReload}>
        {(loans) =>
          loans.map((l) => (
            <Text key={l.id} style={styles.line}>
              {l.player_name} ({l.from_team}): {LOAN_STATUS_LABEL[l.status]}
            </Text>
          ))
        }
      </StateView>
      {squad === null ? (
        <StateView state={teams.state} onRetry={teams.handleReload}>
          {(items) =>
            items.map((r) => (
              <Card
                key={r.team.id}
                title={r.team.name}
                subtitle="Ver jugadores para pedir prestado"
                onPress={() => controller.handleSelectTeam(r.team.id)}
              />
            ))
          }
        </StateView>
      ) : (
        <>
          <PrimaryButton
            label="Elegir otro equipo"
            variant="secondary"
            onPress={() => controller.handleSelectTeam(null)}
          />
          <StateView state={squad.state} onRetry={squad.handleReload}>
            {(detail) => {
              const players = borrowable(detail.members, taken);
              if (players.length === 0)
                return <Text style={styles.line}>Este equipo no tiene jugadores para prestar.</Text>;
              return players.map((m) => (
                <Card key={m.user_id} title={m.display_name} subtitle={m.position ?? 'Sin posición'}>
                  <PrimaryButton
                    label="Pedir prestado"
                    disabled={action.busy}
                    onPress={() => void controller.handleRequest(m.user_id)}
                  />
                </Card>
              ));
            }}
          </StateView>
        </>
      )}
      {action.message ? (
        <Text style={styles.line} accessibilityLiveRegion="polite">
          {action.message}
        </Text>
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  line: { color: colors.text, fontSize: font.small },
  meta: { color: colors.textMuted, fontSize: font.small },
});
