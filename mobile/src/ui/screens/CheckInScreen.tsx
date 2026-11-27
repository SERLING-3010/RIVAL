// Check-in en la cancha: "Llegué" compara tu posición con la de la cancha y no la guarda.

import { StyleSheet, Text } from 'react-native';

import type { CheckInController } from '../../controllers/useCheckIn';
import { checkInStep } from '../../domain/checkInModels';
import { formatLocal } from '../../domain/dateTime';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { colors, font } from '../theme';

interface Props {
  controller: CheckInController;
  now?: Date;
  onBack: () => void;
}

export function CheckInScreen({ controller, now = new Date(), onBack }: Props) {
  return (
    <Screen title="Check-in en la cancha" onBack={onBack}>
      <Text style={styles.meta}>
        Al tocar "Llegué" se lee tu ubicación una sola vez para compararla con la cancha. No se guarda: solo
        queda que llegaste y la hora.
      </Text>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(board) => {
          const step = checkInStep(board, now);
          return (
            <>
              {board.venue_name ? <Text style={styles.title}>{board.venue_name}</Text> : null}
              {step === 'unavailable' ? <Text style={styles.line}>{board.unavailable}</Text> : null}
              {step === 'done' ? <Text style={styles.line}>Ya hiciste check-in en este partido.</Text> : null}
              {step === 'notYet' ? (
                <Text style={styles.line}>El check-in abre el {formatLocal(board.opens_at)}.</Text>
              ) : null}
              {step === 'closed' ? <Text style={styles.line}>El check-in ya cerró.</Text> : null}
              {step === 'open' ? (
                <PrimaryButton
                  label="Llegué"
                  disabled={controller.action.busy}
                  onPress={() => void controller.handleCheckIn()}
                />
              ) : null}
              <Card title={`Llegaron (${board.items.length})`}>
                {board.items.map((i) => (
                  <Text key={i.user_id} style={styles.line}>
                    {i.display_name} · {formatLocal(i.checked_in_at)}
                  </Text>
                ))}
              </Card>
            </>
          );
        }}
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
  title: { color: colors.text, fontSize: font.heading, fontWeight: '700' },
  line: { color: colors.text, fontSize: font.body },
  meta: { color: colors.textMuted, fontSize: font.small },
});
