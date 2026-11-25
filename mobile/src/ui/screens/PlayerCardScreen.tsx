// Ficha del jugador como carta (Sprints 20 y 23): lámina metálica que se voltea para ver la ficha completa.
// Todo sale de partidos con resultado confirmado y planilla; la carta no se compra.

import { Pressable, StyleSheet, Text } from 'react-native';

import type { Loader } from '../../controllers/useLoader';
import type { PlayerCard } from '../../domain/managerModels';
import { CardProgress } from '../components/CardProgress';
import { PlayerCardFoil } from '../components/PlayerCardFoil';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { font, MIN_TOUCH } from '../theme';

interface Props {
  controller: Loader<PlayerCard>;
  onReport: (userId: number, name: string) => void;
  onBadges: (userId: number, name: string) => void;
  onBack: () => void;
}

export function PlayerCardScreen({ controller, onReport, onBadges, onBack }: Props) {
  return (
    <Screen title="Ficha del jugador" tone="dark" onBack={onBack}>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(card) => (
          <>
            <PlayerCardFoil player={card} />
            <Text style={styles.hint}>Toca la carta para ver la ficha completa.</Text>
            <CardProgress card={card.card} />
            <PrimaryButton label="Insignias" onPress={() => onBadges(card.user_id, card.display_name)} />
            <Pressable
              onPress={() => onReport(card.user_id, card.display_name)}
              accessibilityRole="button"
              style={styles.report}
            >
              <Text style={styles.reportText}>Reportar jugador</Text>
            </Pressable>
          </>
        )}
      </StateView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  hint: { color: '#EAF5EE', fontSize: font.small, textAlign: 'center' },
  report: { minHeight: MIN_TOUCH, alignItems: 'center', justifyContent: 'center' },
  reportText: { color: '#FFB48A', fontSize: font.body, fontWeight: '600' },
});
