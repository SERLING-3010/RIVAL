// Comparar dos jugadores: hexágono con seis datos reales y barras enfrentadas.

import { StyleSheet, Text, View } from 'react-native';
import Svg, { Polygon, Text as SvgText } from 'react-native-svg';

import type { PlayerCard } from '../../domain/managerModels';
import { compareAxes } from '../../domain/squadModels';

const A = '#2BD46B';
const B = '#FF7A33';
const CX = 170;
const CY = 125;
const R = 88;

function point(i: number, frac: number): string {
  const angle = ((-90 + i * 60) * Math.PI) / 180;
  return `${(CX + Math.cos(angle) * R * frac).toFixed(1)},${(CY + Math.sin(angle) * R * frac).toFixed(1)}`;
}

export function CompareView({ pair }: { pair: [PlayerCard, PlayerCard] }) {
  const [a, b] = pair;
  const axes = compareAxes(a, b);
  const ring = (frac: number) => axes.map((_, i) => point(i, frac)).join(' ');
  const shape = (pick: 'a' | 'b') => axes.map((x, i) => point(i, Math.min(x[pick] / x.max, 1))).join(' ');
  return (
    <View style={styles.wrap}>
      <View style={styles.heads}>
        <Text style={[styles.head, { borderColor: A }]}>
          <Text style={{ color: A }}>{a.card.media}</Text> {a.display_name}
        </Text>
        <Text style={[styles.head, { borderColor: B }]}>
          <Text style={{ color: B }}>{b.card.media}</Text> {b.display_name}
        </Text>
      </View>
      <Svg width={340} height={250} accessibilityLabel="Hexágono de comparación en seis datos">
        {[1, 0.66, 0.33].map((f) => (
          <Polygon key={f} points={ring(f)} fill="none" stroke="#1D3A29" strokeWidth={1.2} />
        ))}
        <Polygon points={shape('b')} fill="rgba(255,122,51,0.28)" stroke={B} strokeWidth={2.5} />
        <Polygon points={shape('a')} fill="rgba(43,212,107,0.28)" stroke={A} strokeWidth={2.5} />
        {axes.map((x, i) => {
          const [px, py] = point(i, 1.22).split(',').map(Number);
          return (
            <SvgText
              key={x.label}
              x={px}
              y={(py ?? 0) + 4}
              fill="#C7D9CE"
              fontSize={11}
              fontWeight="700"
              textAnchor="middle"
            >
              {x.label}
            </SvgText>
          );
        })}
      </Svg>
      {axes.map((x) => (
        <View key={x.label} style={styles.row}>
          <Text style={[styles.value, styles.right, { color: A }]}>{x.aText}</Text>
          <View style={[styles.track, styles.flip]}>
            <View
              style={[styles.bar, { width: `${Math.round((x.a / x.max) * 100)}%`, backgroundColor: A }]}
            />
          </View>
          <Text style={styles.label}>{x.label}</Text>
          <View style={styles.track}>
            <View
              style={[styles.bar, { width: `${Math.round((x.b / x.max) * 100)}%`, backgroundColor: B }]}
            />
          </View>
          <Text style={[styles.value, { color: B }]}>{x.bText}</Text>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { gap: 8, alignItems: 'center' },
  heads: { flexDirection: 'row', gap: 8, alignSelf: 'stretch' },
  head: {
    flex: 1,
    color: '#EAF5EE',
    fontSize: 14,
    fontWeight: '800',
    borderWidth: 2,
    borderRadius: 12,
    padding: 10,
    backgroundColor: '#0E2217',
  },
  row: { flexDirection: 'row', alignItems: 'center', gap: 6, alignSelf: 'stretch' },
  value: { width: 34, fontSize: 13, fontWeight: '900' },
  right: { textAlign: 'right' },
  track: { flex: 1, height: 8, borderRadius: 4, backgroundColor: '#1D3A29', overflow: 'hidden' },
  flip: { transform: [{ scaleX: -1 }] },
  bar: { height: 8 },
  label: { width: 84, textAlign: 'center', color: '#9DB8A8', fontSize: 11 },
});
