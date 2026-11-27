// Reverso de la carta pequeña: misma lámina que el frente, con posición, partidos, goles, victorias y nivel.

import { StyleSheet, Text } from 'react-native';

import { TIERS } from '../../domain/cardTiers';
import type { SquadCard } from '../../domain/squadModels';
import { TierFoil } from './TierFoil';

export function MiniCardBack({ card }: { card: SquadCard }) {
  const look = TIERS[card.tier];
  const text = { color: look.ink };
  const soft = { color: look.ink, opacity: 0.8 };
  return (
    <TierFoil tier={card.tier} radius={7} frameWidth={1.5} style={styles.face}>
      <Text style={[styles.pos, text]} numberOfLines={1}>
        {(card.position ?? 'Sin posición').toUpperCase()}
      </Text>
      <Text style={[styles.line, soft]}>
        <Text style={[styles.value, text]}>{card.matches}</Text> PJ
      </Text>
      <Text style={[styles.line, soft]}>
        <Text style={[styles.value, text]}>{card.goals}</Text> GOL
      </Text>
      <Text style={[styles.line, soft]}>
        <Text style={[styles.value, text]}>{card.wins}</Text> VIC
      </Text>
      <Text style={[styles.tier, text]} numberOfLines={2}>
        {look.label.toUpperCase()}
      </Text>
    </TierFoil>
  );
}

const styles = StyleSheet.create({
  face: { alignItems: 'center', justifyContent: 'center', gap: 3, padding: 5 },
  pos: { fontSize: 9, fontWeight: '900', letterSpacing: 0.5, maxWidth: 70 },
  line: { fontSize: 10, fontWeight: '700' },
  value: { fontSize: 13, fontWeight: '900' },
  tier: { fontSize: 8, fontWeight: '900', letterSpacing: 1, textAlign: 'center' },
});
