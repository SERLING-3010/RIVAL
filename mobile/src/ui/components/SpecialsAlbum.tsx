// Álbum de las quince especiales (Sprint 23), del jugador o del equipo: ✓ las ganadas, ? las que faltan.

import { StyleSheet, Text, View } from 'react-native';

import type { SpecialCard } from '../../domain/cardModels';
import { albumTiles } from '../../domain/cardProgress';

export function SpecialsAlbum({ specials, title }: { specials: SpecialCard[]; title: string }) {
  const tiles = albumTiles(specials);
  return (
    <View style={styles.wrap}>
      <View style={styles.head}>
        <Text style={styles.label}>{title}</Text>
        <Text style={styles.count}>
          {tiles.filter((t) => t.owned).length} de {tiles.length}
        </Text>
      </View>
      <View style={styles.album}>
        {tiles.map((t) => (
          <View
            key={t.tier}
            accessibilityLabel={`${t.label}: ${t.owned ? 'conseguida' : 'bloqueada'}`}
            style={[styles.tile, t.owned ? { backgroundColor: t.swatch } : styles.locked]}
          >
            <Text style={[styles.tileText, { color: t.owned ? '#06120C' : '#5E7468' }]}>
              {t.owned ? '✓' : '?'}
            </Text>
          </View>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { gap: 8 },
  head: { flexDirection: 'row', justifyContent: 'space-between' },
  label: { color: '#9DB8A8', fontSize: 12, fontWeight: '700', letterSpacing: 1 },
  count: { color: '#EAF5EE', fontSize: 12, fontWeight: '700' },
  album: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  tile: { width: 32, height: 40, borderRadius: 7, alignItems: 'center', justifyContent: 'center' },
  locked: { backgroundColor: '#0E2217', borderWidth: 1, borderStyle: 'dashed', borderColor: '#2F4A3B' },
  tileText: { fontSize: 11, fontWeight: '900' },
});
