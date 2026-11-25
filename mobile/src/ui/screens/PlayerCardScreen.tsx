// Ficha del jugador: estadísticas reales de partidos con resultado confirmado y planilla.

import { StyleSheet, Text } from 'react-native';

import type { Loader } from '../../controllers/useLoader';
import type { PlayerCard } from '../../domain/managerModels';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { colors, font } from '../theme';

interface Props {
  controller: Loader<PlayerCard>;
  onReport: (userId: number, name: string) => void;
  onBadges: (userId: number, name: string) => void;
  onBack: () => void;
}

export function PlayerCardScreen({ controller, onReport, onBadges, onBack }: Props) {
  return (
    <Screen title="Ficha del jugador" onBack={onBack}>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(card) => (
          <>
            <Text style={styles.title}>{card.display_name}</Text>
            <Text style={styles.meta}>
              {card.position ?? 'Sin posición'} · {card.teams.map((t) => t.name).join(', ') || 'Sin equipo'}
            </Text>
            <Card title="Estadísticas reales">
              <Text style={styles.line}>Partidos jugados: {card.matches}</Text>
              <Text style={styles.line}>Goles: {card.goals}</Text>
              <Text style={styles.line}>
                Ganados {card.wins} · Empatados {card.draws} · Perdidos {card.losses}
              </Text>
              <Text style={styles.line}>
                Valoración de compañeros:{' '}
                {card.rating_average === null
                  ? 'sin votos aún'
                  : `${card.rating_average} (${card.rating_votes} voto${card.rating_votes === 1 ? '' : 's'})`}
              </Text>
            </Card>
            <Text style={styles.meta}>
              Solo cuentan partidos con resultado confirmado por ambos equipos y con el jugador en la
              planilla.
            </Text>
            <PrimaryButton label="Insignias" onPress={() => onBadges(card.user_id, card.display_name)} />
            <PrimaryButton
              label="Reportar jugador"
              variant="secondary"
              onPress={() => onReport(card.user_id, card.display_name)}
            />
          </>
        )}
      </StateView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  title: { color: colors.text, fontSize: font.heading, fontWeight: '700' },
  line: { color: colors.text, fontSize: font.body },
  meta: { color: colors.textMuted, fontSize: font.small },
});
