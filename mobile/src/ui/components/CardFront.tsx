// Frente de la carta: lámina metálica, media, posición, escudo, silueta y seis estadísticas reales.

import { LinearGradient } from 'expo-linear-gradient';
import { StyleSheet, Text, View } from 'react-native';

import { frontStats, initials, TIER_FOIL, TIER_LABEL } from '../../domain/cardModels';
import type { PlayerCard } from '../../domain/managerModels';
import { CardSheen } from './CardSheen';

const INK = '#1A1206';

export function CardFront({ player }: { player: PlayerCard }) {
  const team = player.teams[0];
  return (
    <LinearGradient
      colors={TIER_FOIL[player.card.tier]}
      locations={[0, 0.28, 0.48, 0.72, 1]}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={styles.face}
    >
      <CardSheen />
      <View style={styles.inner} />
      <View style={styles.left}>
        <Text style={styles.media}>{player.card.media}</Text>
        <Text style={styles.pos}>{(player.position ?? '—').slice(0, 3).toUpperCase()}</Text>
        <View style={styles.crest}>
          <Text style={styles.crestText}>{team ? initials(team.name) : '—'}</Text>
        </View>
        <Text style={styles.tier}>{TIER_LABEL[player.card.tier].toUpperCase()}</Text>
      </View>
      <View style={styles.photo} accessibilityLabel="Sin foto: silueta del jugador">
        <View style={styles.head} />
        <View style={styles.body} />
      </View>
      <View style={styles.bottom}>
        <Text style={styles.name} numberOfLines={1} adjustsFontSizeToFit>
          {player.display_name.toUpperCase()}
        </Text>
        <View style={styles.rule} />
        <View style={styles.stats}>
          {frontStats(player).map((s) => (
            <Text key={s.label} style={styles.stat}>
              <Text style={styles.statValue}>{s.value}</Text> {s.label}
            </Text>
          ))}
        </View>
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  face: { flex: 1, borderRadius: 22, overflow: 'hidden', backfaceVisibility: 'hidden' },
  inner: {
    position: 'absolute',
    top: 7,
    left: 7,
    right: 7,
    bottom: 7,
    borderRadius: 17,
    borderWidth: 1,
    borderColor: 'rgba(26,18,6,0.25)',
  },
  left: { position: 'absolute', left: 22, top: 26, alignItems: 'center', gap: 2 },
  media: { color: INK, fontSize: 52, fontWeight: '900', lineHeight: 54 },
  pos: { color: INK, fontSize: 18, fontWeight: '800', letterSpacing: 1 },
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
  tier: { marginTop: 6, color: INK, fontSize: 9, fontWeight: '900', letterSpacing: 1.4 },
  photo: { position: 'absolute', right: 18, top: 28, width: 150, height: 180, alignItems: 'center' },
  head: { width: 76, height: 76, borderRadius: 38, backgroundColor: 'rgba(26,18,6,0.28)', marginTop: 20 },
  body: {
    width: 140,
    height: 78,
    borderTopLeftRadius: 70,
    borderTopRightRadius: 70,
    backgroundColor: 'rgba(26,18,6,0.28)',
    marginTop: 6,
  },
  bottom: { position: 'absolute', left: 0, right: 0, top: 220, alignItems: 'center', gap: 8 },
  name: { color: INK, fontSize: 26, fontWeight: '900', letterSpacing: 0.6, maxWidth: 230 },
  rule: { width: 200, height: 1, backgroundColor: 'rgba(26,18,6,0.3)' },
  stats: { flexDirection: 'row', flexWrap: 'wrap', width: 210, rowGap: 2 },
  stat: { width: '50%', color: INK, fontSize: 18, textAlign: 'center' },
  statValue: { fontWeight: '900' },
});
