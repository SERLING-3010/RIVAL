// Mercado de fichajes: jugadores transferibles del mismo deporte en la ciudad. El jugador siempre acepta.

import { useState } from 'react';
import { StyleSheet, Text } from 'react-native';

import type { MarketController } from '../../controllers/useManager';
import { formatCoins } from '../../domain/managerRules';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { TextField } from '../components/TextField';
import { colors, font } from '../theme';

interface Props {
  controller: MarketController;
  balance: number;
  onOpenCard: (userId: number) => void;
  onBack: () => void;
}

export function MarketScreen({ controller, balance, onOpenCard, onBack }: Props) {
  const [amounts, setAmounts] = useState<Record<number, string>>({});
  const [errors, setErrors] = useState<Record<number, string | null>>({});
  const send = async (playerId: number) => {
    const error = await controller.handleOffer(playerId, amounts[playerId] ?? '', balance);
    setErrors((e) => ({ ...e, [playerId]: error }));
  };
  return (
    <Screen title="Mercado de fichajes" onBack={onBack}>
      <Text style={styles.meta}>
        Tu presupuesto: {formatCoins(balance)}. Primero acepta el DT del jugador y después el jugador; sin las
        dos aceptaciones no se mueve nada.
      </Text>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(items) =>
          items.map((item) => (
            <Card
              key={item.player_id}
              title={item.display_name}
              subtitle={`${item.team.name}${item.position ? ` · ${item.position}` : ''} · ${item.matches} PJ · ${item.goals} goles`}
              onPress={() => onOpenCard(item.player_id)}
            >
              <TextField
                label={`Oferta por ${item.display_name} (monedas RIVAL)`}
                keyboardType="number-pad"
                value={amounts[item.player_id] ?? ''}
                onChangeText={(v) => setAmounts((a) => ({ ...a, [item.player_id]: v }))}
                error={errors[item.player_id] ?? undefined}
              />
              <PrimaryButton
                label="Ofertar"
                disabled={controller.action.busy}
                onPress={() => void send(item.player_id)}
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
