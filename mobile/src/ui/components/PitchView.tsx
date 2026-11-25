// Titulares sobre la cancha, por líneas de la formación (arquero abajo), y suplentes debajo.

import { StyleSheet, Text, View } from 'react-native';

import type { Squad } from '../../domain/squadModels';
import { pitchRows } from '../../domain/squadModels';
import { MiniCard } from './MiniCard';

interface Props {
  squad: Squad;
  onOpen: (userId: number) => void;
}

export function PitchView({ squad, onOpen }: Props) {
  const byId = new Map(squad.members.map((m) => [m.user_id, m]));
  const rows = pitchRows(squad.formation, squad.starters);
  const subs = squad.subs.map((id) => byId.get(id)).filter((m) => m !== undefined);
  return (
    <View style={styles.wrap}>
      {squad.suggested ? (
        <Text style={styles.note}>
          Alineación sugerida por media: aún no hay una guardada para el próximo partido.
        </Text>
      ) : null}
      <View
        style={[styles.pitch, { height: Math.max(440, rows.length * 140 + 20) }]}
        accessibilityLabel="Cancha con los titulares"
      >
        {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => (
          <View key={i} style={[styles.stripe, i % 2 === 1 ? styles.stripeDark : null]} />
        ))}
        <View style={styles.midLine} />
        <View style={styles.circle} />
        <View style={styles.rows}>
          {rows.map((row, r) => (
            <View key={r} style={styles.row}>
              {row.map((s) => {
                const card = byId.get(s.user_id);
                return card ? (
                  <MiniCard
                    key={s.user_id}
                    card={card}
                    teamName={squad.team.name}
                    tag={s.position}
                    onOpen={onOpen}
                  />
                ) : null;
              })}
            </View>
          ))}
        </View>
      </View>
      <Text style={styles.hint}>Toca una carta para voltearla; mantenla presionada para ver la ficha.</Text>
      {subs.length > 0 ? (
        <View style={styles.subs}>
          <Text style={styles.subsLabel}>SUPLENTES</Text>
          {subs.map((m) => (
            <Text key={m.user_id} style={styles.sub} onPress={() => onOpen(m.user_id)}>
              <Text style={styles.subMedia}>{m.media}</Text> {m.display_name}
            </Text>
          ))}
        </View>
      ) : null}
    </View>
  );
}

const LINE = 'rgba(255,255,255,0.35)';
const styles = StyleSheet.create({
  wrap: { gap: 10 },
  note: { color: '#FFB48A', fontSize: 12 },
  hint: { color: '#9DB8A8', fontSize: 12 },
  pitch: { borderRadius: 18, overflow: 'hidden', borderWidth: 2, borderColor: LINE },
  stripe: { flex: 1, backgroundColor: '#0F4A2A' },
  stripeDark: { backgroundColor: '#0D4225' },
  midLine: { position: 'absolute', left: 0, right: 0, top: '50%', height: 2, backgroundColor: LINE },
  circle: {
    position: 'absolute',
    left: '50%',
    top: '50%',
    width: 80,
    height: 80,
    marginLeft: -40,
    marginTop: -40,
    borderRadius: 40,
    borderWidth: 2,
    borderColor: LINE,
  },
  rows: { ...StyleSheet.absoluteFill, justifyContent: 'space-around', paddingVertical: 10 },
  row: { flexDirection: 'row', justifyContent: 'space-evenly' },
  subs: { flexDirection: 'row', flexWrap: 'wrap', alignItems: 'center', gap: 8 },
  subsLabel: { color: '#9DB8A8', fontSize: 11, fontWeight: '700', letterSpacing: 1 },
  sub: {
    color: '#EAF5EE',
    fontSize: 13,
    backgroundColor: '#0E2217',
    borderWidth: 1,
    borderColor: '#1D3A29',
    borderRadius: 10,
    paddingHorizontal: 10,
    paddingVertical: 8,
    overflow: 'hidden',
  },
  subMedia: { fontWeight: '900' },
});
