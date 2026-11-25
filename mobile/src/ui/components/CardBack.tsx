// Reverso de la carta: misma lámina que el frente, con récord, últimos partidos, insignias y avance.

import { StyleSheet, Text, View } from 'react-native';

import type { RecentResult } from '../../domain/cardModels';
import { goalsPerMatch, nextTierText, RESULT_LABEL } from '../../domain/cardModels';
import { tierProgress } from '../../domain/cardProgress';
import { TIERS } from '../../domain/cardTiers';
import type { PlayerCard } from '../../domain/managerModels';
import { shade, TierFoil } from './TierFoil';

const RESULT_COLOR: Record<RecentResult, string> = { W: '#2BD46B', D: '#6B7F74', L: '#FF7A33' };

export function CardBack({ player }: { player: PlayerCard }) {
  const c = player.card;
  const ink = TIERS[c.display_tier].ink;
  const text = { color: ink };
  const soft = { color: ink, opacity: 0.75 };
  const panel = { backgroundColor: shade(ink, 0.14) };
  const done = tierProgress(c);
  const box = (value: string, label: string) => (
    <View style={[styles.box, panel]}>
      <Text style={[styles.boxValue, text]}>{value}</Text>
      <Text style={[styles.boxLabel, soft]}>{label}</Text>
    </View>
  );
  return (
    <TierFoil tier={c.display_tier} radius={22} style={styles.face}>
      <Text style={[styles.name, text]} numberOfLines={1}>
        {player.display_name.toUpperCase()}
      </Text>
      <Text style={[styles.small, soft]}>{player.teams.map((t) => t.name).join(' · ') || 'Sin equipo'}</Text>
      <View style={styles.row}>
        {box(`${player.wins}-${player.draws}-${player.losses}`, 'G-E-P')}
        {box(goalsPerMatch(player), 'G/P')}
        {box(String(player.rating_votes), 'VOTOS')}
      </View>
      <Text style={[styles.section, soft]}>ÚLTIMOS PARTIDOS</Text>
      <View style={styles.row}>
        {c.recent.length === 0 ? (
          <Text style={[styles.small, soft]}>Aún sin partidos confirmados.</Text>
        ) : null}
        {c.recent.map((r, i) => (
          <View key={`${r}-${i}`} style={[styles.result, { backgroundColor: RESULT_COLOR[r] }]}>
            <Text style={styles.resultText}>{RESULT_LABEL[r]}</Text>
          </View>
        ))}
      </View>
      <Text style={[styles.section, soft]}>INSIGNIAS</Text>
      <View style={styles.chips}>
        {c.badges.length === 0 ? <Text style={[styles.small, soft]}>Todavía ninguna.</Text> : null}
        {c.badges.slice(0, 6).map((b) => (
          <Text key={b} style={[styles.chip, text, { borderColor: shade(ink, 0.5) }]}>
            {b}
          </Text>
        ))}
      </View>
      <Text style={[styles.section, soft]}>{nextTierText(c).toUpperCase()}</Text>
      <View style={[styles.track, { backgroundColor: shade(ink, 0.2) }]}>
        <View style={[styles.fill, { width: `${Math.round(done * 100)}%`, backgroundColor: ink }]} />
      </View>
      <Text style={[styles.foot, soft]}>
        Datos de partidos confirmados. La carta sube jugando; no se compra.
      </Text>
    </TierFoil>
  );
}

const styles = StyleSheet.create({
  face: { padding: 20, gap: 8 },
  name: { fontSize: 22, fontWeight: '900' },
  small: { fontSize: 11 },
  row: { flexDirection: 'row', gap: 6 },
  box: { flex: 1, borderRadius: 8, paddingVertical: 6, alignItems: 'center' },
  boxValue: { fontSize: 18, fontWeight: '900' },
  boxLabel: { fontSize: 9, fontWeight: '700' },
  section: { fontSize: 10, fontWeight: '800', letterSpacing: 1 },
  result: { flex: 1, height: 26, borderRadius: 6, alignItems: 'center', justifyContent: 'center' },
  resultText: { color: '#06120C', fontSize: 12, fontWeight: '900' },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: 5 },
  chip: {
    fontSize: 10,
    fontWeight: '700',
    borderWidth: 1,
    borderRadius: 999,
    paddingHorizontal: 8,
    paddingVertical: 3,
  },
  track: { height: 8, borderRadius: 4, overflow: 'hidden' },
  fill: { height: 8 },
  foot: { fontSize: 10 },
});
