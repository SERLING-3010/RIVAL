// Reverso de la carta: ficha completa con récord, últimos partidos, insignias y avance de nivel.

import { StyleSheet, Text, View } from 'react-native';

import { goalsPerMatch, nextTierText, RESULT_LABEL } from '../../domain/cardModels';
import type { RecentResult } from '../../domain/cardModels';
import type { PlayerCard } from '../../domain/managerModels';

const RESULT_COLOR: Record<RecentResult, string> = { W: '#2BD46B', D: '#6B7F74', L: '#FF7A33' };

export function CardBack({ player }: { player: PlayerCard }) {
  const c = player.card;
  const done = c.next_tier === null ? 1 : Math.max(0, 1 - c.matches_to_next / 10);
  return (
    <View style={styles.face}>
      <Text style={styles.name} numberOfLines={1}>
        {player.display_name.toUpperCase()}
      </Text>
      <Text style={styles.muted}>{player.teams.map((t) => t.name).join(' · ') || 'Sin equipo'}</Text>
      <View style={styles.row}>
        <Box value={`${player.wins}-${player.draws}-${player.losses}`} label="G-E-P" />
        <Box value={goalsPerMatch(player)} label="GOLES/PARTIDO" />
        <Box value={String(player.rating_votes)} label="VOTOS" />
      </View>
      <Text style={styles.section}>ÚLTIMOS PARTIDOS</Text>
      <View style={styles.row}>
        {c.recent.length === 0 ? <Text style={styles.muted}>Aún sin partidos confirmados.</Text> : null}
        {c.recent.map((r, i) => (
          <View key={`${r}-${i}`} style={[styles.result, { backgroundColor: RESULT_COLOR[r] }]}>
            <Text style={styles.resultText}>{RESULT_LABEL[r]}</Text>
          </View>
        ))}
      </View>
      <Text style={styles.section}>INSIGNIAS</Text>
      <View style={styles.chips}>
        {c.badges.length === 0 ? <Text style={styles.muted}>Todavía ninguna.</Text> : null}
        {c.badges.slice(0, 6).map((b) => (
          <Text key={b} style={styles.chip}>
            {b}
          </Text>
        ))}
      </View>
      <Text style={styles.section}>{nextTierText(c).toUpperCase()}</Text>
      <View style={styles.track}>
        <View style={[styles.fill, { width: `${Math.round(done * 100)}%` }]} />
      </View>
      <Text style={styles.foot}>Datos de partidos confirmados. La carta sube jugando; no se compra.</Text>
    </View>
  );
}

function Box({ value, label }: { value: string; label: string }) {
  return (
    <View style={styles.box}>
      <Text style={styles.boxValue}>{value}</Text>
      <Text style={styles.boxLabel}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  face: {
    flex: 1,
    borderRadius: 22,
    borderWidth: 1,
    borderColor: '#2BD46B',
    backgroundColor: '#0F2A1C',
    padding: 20,
    gap: 8,
    backfaceVisibility: 'hidden',
  },
  name: { color: '#EAF5EE', fontSize: 22, fontWeight: '900' },
  muted: { color: '#9DB8A8', fontSize: 11 },
  row: { flexDirection: 'row', gap: 6 },
  box: {
    flex: 1,
    backgroundColor: 'rgba(255,255,255,0.06)',
    borderRadius: 8,
    paddingVertical: 6,
    alignItems: 'center',
  },
  boxValue: { color: '#EAF5EE', fontSize: 18, fontWeight: '900' },
  boxLabel: { color: '#9DB8A8', fontSize: 9 },
  section: { color: '#9DB8A8', fontSize: 10, fontWeight: '700', letterSpacing: 1 },
  result: { flex: 1, height: 26, borderRadius: 6, alignItems: 'center', justifyContent: 'center' },
  resultText: { color: '#06120C', fontSize: 12, fontWeight: '900' },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: 5 },
  chip: {
    color: '#A6F0C2',
    fontSize: 10,
    fontWeight: '700',
    borderWidth: 1,
    borderColor: '#2BD46B',
    borderRadius: 999,
    paddingHorizontal: 8,
    paddingVertical: 3,
  },
  track: { height: 8, borderRadius: 4, backgroundColor: '#1D3A29', overflow: 'hidden' },
  fill: { height: 8, backgroundColor: '#2BD46B' },
  foot: { color: '#9DB8A8', fontSize: 10 },
});
