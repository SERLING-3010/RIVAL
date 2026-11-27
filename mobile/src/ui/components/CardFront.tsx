// Frente de la carta: lámina del nivel con sus efectos, media, posición, escudo, silueta y seis estadísticas.

import { StyleSheet, Text, View } from 'react-native';

import type { CardFaceData } from '../../domain/cardModels';
import { TIERS } from '../../domain/cardTiers';
import { TierEmblem } from './TierEmblem';
import { shade, TierFoil } from './TierFoil';

/** La carta grande de la ficha; la plantilla la dibuja igual, a escala (ScaledCard). */
export function CardFront({ face }: { face: CardFaceData }) {
  const look = TIERS[face.tier];
  const ink = { color: look.ink };
  const glow = look.emblem === 'neon' ? styles.neonText : null;
  return (
    <TierFoil tier={face.tier} radius={22}>
      <View style={[styles.inner, { borderColor: shade(look.ink, 0.3) }]} />
      <View style={styles.left}>
        <Text style={[styles.media, ink, glow]} numberOfLines={1}>
          {face.media}
        </Text>
        <Text style={[styles.pos, ink, glow]}>{face.position}</Text>
        <View style={styles.crest}>
          <Text style={styles.crestText}>{face.crest}</Text>
        </View>
        <Text style={[styles.tier, ink]} numberOfLines={2}>
          {look.label.toUpperCase()}
        </Text>
      </View>
      {look.emblem ? (
        <View style={styles.photo}>
          <TierEmblem kind={look.emblem} color={look.ink} />
        </View>
      ) : (
        <View style={styles.photo} accessibilityLabel="Sin foto: silueta del jugador">
          <View style={[styles.head, { backgroundColor: shade(look.ink, 0.28) }]} />
          <View style={[styles.body, { backgroundColor: shade(look.ink, 0.28) }]} />
        </View>
      )}
      <View style={styles.bottom}>
        <Text style={[styles.name, ink, glow]} numberOfLines={1} adjustsFontSizeToFit>
          {face.name.toUpperCase()}
        </Text>
        <View style={[styles.rule, { backgroundColor: shade(look.ink, 0.35) }]} />
        <View style={styles.stats}>
          {face.stats.map((s) => (
            <Text key={s.label} style={[styles.stat, ink]}>
              <Text style={styles.statValue}>{s.value}</Text> {s.label}
            </Text>
          ))}
        </View>
      </View>
    </TierFoil>
  );
}

const styles = StyleSheet.create({
  inner: {
    position: 'absolute',
    top: 7,
    left: 7,
    right: 7,
    bottom: 7,
    borderRadius: 17,
    borderWidth: 1,
  },
  left: { position: 'absolute', left: 18, top: 26, width: 84, alignItems: 'center', gap: 2 },
  media: { fontSize: 52, fontWeight: '900', lineHeight: 54 },
  pos: { fontSize: 18, fontWeight: '800', letterSpacing: 1 },
  neonText: { textShadowColor: '#2BD46B', textShadowRadius: 10, textShadowOffset: { width: 0, height: 0 } },
  crest: {
    marginTop: 8,
    width: 34,
    height: 34,
    borderRadius: 10,
    backgroundColor: '#0B6B3A',
    alignItems: 'center',
    justifyContent: 'center',
  },
  crestText: { color: '#FFFFFF', fontSize: 14, fontWeight: '900' },
  tier: { marginTop: 6, fontSize: 9, fontWeight: '900', letterSpacing: 1.2, textAlign: 'center' },
  photo: {
    position: 'absolute',
    right: 18,
    top: 28,
    width: 150,
    height: 180,
    alignItems: 'center',
    justifyContent: 'center',
  },
  head: { width: 76, height: 76, borderRadius: 38, marginTop: 20 },
  body: { width: 140, height: 78, borderTopLeftRadius: 70, borderTopRightRadius: 70, marginTop: 6 },
  bottom: { position: 'absolute', left: 0, right: 0, top: 220, alignItems: 'center', gap: 8 },
  name: { fontSize: 26, fontWeight: '900', letterSpacing: 0.6, maxWidth: 230 },
  rule: { width: 200, height: 1 },
  stats: { flexDirection: 'row', flexWrap: 'wrap', width: 210, rowGap: 2 },
  stat: { width: '50%', fontSize: 18, textAlign: 'center' },
  statValue: { fontWeight: '900' },
});
