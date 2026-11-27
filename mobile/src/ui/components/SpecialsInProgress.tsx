// Las cartas especiales más cercanas (Sprint 23), del jugador o del equipo: media mínima y cada hazaña.

import { StyleSheet, Text, View } from 'react-native';

import type { SpecialCard } from '../../domain/cardModels';
import { nextSpecials } from '../../domain/cardProgress';
import { TIERS } from '../../domain/cardTiers';
import { font } from '../theme';

interface Props {
  media: number;
  specials: SpecialCard[];
  note: string; // aclaración al pie: de dónde salen las hazañas
}

export function SpecialsInProgress({ media, specials, note }: Props) {
  const next = nextSpecials({ media, specials });
  if (next.length === 0) {
    return (
      <View style={styles.box}>
        <Text style={styles.title}>¡Tienes las quince especiales!</Text>
      </View>
    );
  }
  return (
    <View style={styles.box}>
      <Text style={styles.label}>PRÓXIMAS ESPECIALES</Text>
      {next.map((s) => (
        <View key={s.code} style={styles.item}>
          <Text style={[styles.name, { color: TIERS[s.code].swatch }]}>{s.label}</Text>
          <Text style={[styles.line, s.mediaOk ? styles.ok : null]}>
            {s.mediaOk ? '✓' : '·'} Media {s.minMedia}
            {s.mediaOk ? '' : ` (tienes ${media})`}
          </Text>
          {s.goals.map((g) => {
            const done = g.current >= g.target;
            const pct = `${Math.round(Math.min(1, g.current / g.target) * 100)}%` as const;
            return (
              <View key={g.label} style={styles.goal}>
                <Text style={[styles.line, done ? styles.ok : null]}>
                  {done ? '✓' : '·'} {g.label}: {g.current} / {g.target}
                </Text>
                <View style={styles.track}>
                  <View style={[styles.fill, { width: pct, backgroundColor: TIERS[s.code].swatch }]} />
                </View>
              </View>
            );
          })}
        </View>
      ))}
      <Text style={styles.muted}>{note}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  box: {
    backgroundColor: '#0E2217',
    borderWidth: 1,
    borderColor: '#1D3A29',
    borderRadius: 16,
    padding: 14,
    gap: 10,
  },
  label: { color: '#9DB8A8', fontSize: 12, fontWeight: '700', letterSpacing: 1 },
  title: { color: '#EAF5EE', fontSize: font.body, fontWeight: '800' },
  item: { gap: 4 },
  name: { fontSize: font.body, fontWeight: '900' },
  goal: { gap: 3 },
  line: { color: '#C9D8CF', fontSize: 12 },
  ok: { color: '#2BD46B', fontWeight: '800' },
  track: { height: 6, borderRadius: 3, backgroundColor: '#1D3A29', overflow: 'hidden' },
  fill: { height: 6 },
  muted: { color: '#9DB8A8', fontSize: 11 },
});
