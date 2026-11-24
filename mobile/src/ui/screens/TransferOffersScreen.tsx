// Ofertas de traspaso que esperan mi decisión. Nadie me cambia de equipo sin que yo acepte.

import { Alert, StyleSheet, Text } from 'react-native';

import type { MyOffersController } from '../../controllers/useManager';
import { formatCoins } from '../../domain/managerRules';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { colors, font } from '../theme';

interface Props {
  controller: MyOffersController;
  onBack: () => void;
}

export function TransferOffersScreen({ controller, onBack }: Props) {
  const busy = controller.action.busy;
  const confirm = (offerId: number, team: string) =>
    Alert.alert(`¿Pasar a ${team}?`, 'Saldrás de tu equipo actual y entrarás como jugador al nuevo.', [
      { text: 'Pensarlo', style: 'cancel' },
      { text: 'Aceptar traspaso', onPress: () => void controller.handleDecide(offerId, true) },
    ]);
  return (
    <Screen title="Ofertas de traspaso" onBack={onBack}>
      <Text style={styles.meta}>Tu DT ya aceptó estas ofertas. Tú decides si te vas.</Text>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(offers) =>
          offers.map((o) => (
            <Card
              key={o.id}
              title={`${o.to_team.name} quiere ficharte`}
              subtitle={`De ${o.from_team.name} · ${formatCoins(o.amount)} entre equipos`}
            >
              <PrimaryButton
                label="Aceptar traspaso"
                disabled={busy}
                onPress={() => confirm(o.id, o.to_team.name)}
              />
              <PrimaryButton
                label="Rechazar"
                variant="secondary"
                disabled={busy}
                onPress={() => void controller.handleDecide(o.id, false)}
              />
            </Card>
          ))
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
  meta: { color: colors.textMuted, fontSize: font.small },
  line: { color: colors.text, fontSize: font.small },
});
