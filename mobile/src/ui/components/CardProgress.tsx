// Mi progreso (Sprint 23): carta básica por media, especiales en curso, valor de mercado y álbum.

import { StyleSheet, Text, View } from 'react-native';

import type { CardFace } from '../../domain/cardModels';
import { nextTierText } from '../../domain/cardModels';
import { coinsText, tierProgress } from '../../domain/cardProgress';
import { TIERS } from '../../domain/cardTiers';
import { font } from '../theme';
import { SpecialsAlbum } from './SpecialsAlbum';
import { SpecialsInProgress } from './SpecialsInProgress';

export function CardProgress({ card }: { card: CardFace }) {
  const next = card.next_tier;
  const pct = `${Math.round(tierProgress(card) * 100)}%` as const;
  return (
    <View style={styles.wrap}>
      <View style={styles.box}>
        <Text style={styles.label}>CARTA BÁSICA · {TIERS[card.tier].label.toUpperCase()}</Text>
        <Text style={styles.title}>{nextTierText(card)}</Text>
        {next ? (
          <View style={styles.track} accessibilityLabel={`Avance hacia ${TIERS[next].label}: ${pct}`}>
            <View style={[styles.fill, { width: pct, backgroundColor: TIERS[next].swatch }]} />
          </View>
        ) : null}
        <Text style={styles.muted}>Sale de tu media: sube y baja con ella.</Text>
      </View>
      <SpecialsInProgress
        media={card.media}
        specials={card.specials}
        note="Goles con tipo (chilena, olímpico, tiro libre…) cuentan cuando el rival los confirma. Una especial ganada es tuya para siempre."
      />
      <View style={[styles.box, styles.value]}>
        <Text style={styles.label}>VALOR DE MERCADO</Text>
        <Text style={styles.coins}>≈ {coinsText(card.market_value)}</Text>
        <Text style={styles.muted}>
          Sube con tu media, tus cartas y tus últimos 5 partidos. Monedas RIVAL virtuales: se ganan jugando,
          no se compran ni se venden.
        </Text>
      </View>
      <SpecialsAlbum specials={card.specials} title="ÁLBUM DE ESPECIALES" />
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { alignSelf: 'stretch', gap: 12 },
  box: {
    backgroundColor: '#0E2217',
    borderWidth: 1,
    borderColor: '#1D3A29',
    borderRadius: 16,
    padding: 14,
    gap: 8,
  },
  value: { borderColor: '#2BD46B' },
  title: { color: '#EAF5EE', fontSize: font.body, fontWeight: '800' },
  muted: { color: '#9DB8A8', fontSize: 12 },
  label: { color: '#9DB8A8', fontSize: 12, fontWeight: '700', letterSpacing: 1 },
  coins: { color: '#F6DE92', fontSize: 30, fontWeight: '900' },
  track: { height: 10, borderRadius: 5, backgroundColor: '#1D3A29', overflow: 'hidden' },
  fill: { height: 10 },
});
