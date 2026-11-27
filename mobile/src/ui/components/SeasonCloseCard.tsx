// Cierre de temporada (Sprint 23): el organizador la cierra y gana el primero de la tabla.

import { Alert, StyleSheet, Text } from 'react-native';

import type { LeagueDetail } from '../../domain/leagueModels';
import { colors, font } from '../theme';
import { Card } from './Card';
import { PrimaryButton } from './PrimaryButton';

interface Props {
  detail: LeagueDetail;
  busy: boolean;
  onClose: () => void;
}

export function SeasonCloseCard({ detail, busy, onClose }: Props) {
  if (detail.champion) {
    return (
      <Card title={`Campeón ${detail.league.season}`} badge="Temporada cerrada">
        <Text style={styles.champion}>🏆 {detail.champion.name}</Text>
        <Text style={styles.meta}>Su barra de equipo cuenta este título para sus cartas especiales.</Text>
      </Card>
    );
  }
  if (detail.my_role !== 'ORGANIZER') return null;
  const confirm = () =>
    Alert.alert(
      '¿Cerrar la temporada?',
      'Gana el primero de la tabla. Todos los partidos deben tener resultado confirmado o estar cancelados. No se puede reabrir.',
      [
        { text: 'Todavía no', style: 'cancel' },
        { text: 'Cerrar temporada', style: 'destructive', onPress: onClose },
      ],
    );
  return (
    <Card title="Fin de temporada">
      <Text style={styles.meta}>Cuando se jueguen todos los partidos, ciérrala para coronar al campeón.</Text>
      <PrimaryButton label="Cerrar temporada" variant="secondary" disabled={busy} onPress={confirm} />
    </Card>
  );
}

const styles = StyleSheet.create({
  champion: { color: colors.text, fontSize: font.heading, fontWeight: '800' },
  meta: { color: colors.textMuted, fontSize: font.small },
});
