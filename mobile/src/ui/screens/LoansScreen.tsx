// Préstamos que esperan mi decisión: primero el DT del equipo dueño, después el jugador.

import { StyleSheet, Text } from 'react-native';

import type { MyLoansController } from '../../controllers/useLoans';
import { formatLocal } from '../../domain/dateTime';
import { LOAN_STATUS_LABEL } from '../../domain/loanModels';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { colors, font } from '../theme';

interface Props {
  controller: MyLoansController;
  onBack: () => void;
}

export function LoansScreen({ controller, onBack }: Props) {
  const busy = controller.action.busy;
  return (
    <Screen title="Préstamos" onBack={onBack}>
      <Text style={styles.meta}>
        Un préstamo vale para un solo partido. Nadie juega prestado sin aceptarlo.
      </Text>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(items) =>
          items.map((loan) => {
            const player = loan.status === 'PENDING_PLAYER';
            return (
              <Card
                key={loan.id}
                title={`${loan.player_name}: de ${loan.from_team} a ${loan.to_team}`}
                subtitle={`Partido: ${formatLocal(loan.kickoff_at)}`}
                badge={LOAN_STATUS_LABEL[loan.status]}
              >
                <PrimaryButton
                  label={player ? 'Acepto jugar prestado' : 'Prestar al jugador'}
                  disabled={busy}
                  onPress={() =>
                    void controller.handleDecide(loan.id, player ? 'player-accept' : 'owner-accept')
                  }
                />
                <PrimaryButton
                  label="Rechazar"
                  variant="secondary"
                  disabled={busy}
                  onPress={() =>
                    void controller.handleDecide(loan.id, player ? 'player-reject' : 'owner-reject')
                  }
                />
              </Card>
            );
          })
        }
      </StateView>
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
});
