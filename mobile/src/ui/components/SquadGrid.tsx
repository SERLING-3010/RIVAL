// Todas las cartas del equipo en cuadrícula, ordenables por media, posición o partidos.

import { useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import type { SquadCard, SquadSort } from '../../domain/squadModels';
import { sortMembers } from '../../domain/squadModels';
import { MIN_TOUCH } from '../theme';
import { MiniCard } from './MiniCard';

const SORTS: { value: SquadSort; label: string }[] = [
  { value: 'media', label: 'Media' },
  { value: 'position', label: 'Posición' },
  { value: 'matches', label: 'Partidos' },
];

interface Props {
  members: SquadCard[];
  teamName: string;
  onOpen: (userId: number) => void;
}

export function SquadGrid({ members, teamName, onOpen }: Props) {
  const [sort, setSort] = useState<SquadSort>('media');
  const sorted = sortMembers(members, sort);
  return (
    <View style={styles.wrap}>
      <View style={styles.sorts} accessibilityRole="radiogroup" accessibilityLabel="Ordenar por">
        <Text style={styles.sortLabel}>Ordenar:</Text>
        {SORTS.map((s) => (
          <Pressable
            key={s.value}
            onPress={() => setSort(s.value)}
            accessibilityRole="radio"
            accessibilityState={{ checked: sort === s.value }}
            style={[styles.chip, sort === s.value ? styles.chipOn : null]}
          >
            <Text style={[styles.chipText, sort === s.value ? styles.chipTextOn : null]}>{s.label}</Text>
          </Pressable>
        ))}
      </View>
      <View style={styles.grid}>
        {sorted.map((m) => (
          <MiniCard key={m.user_id} card={m} teamName={teamName} onOpen={onOpen} />
        ))}
      </View>
      <Text style={styles.hint}>Toca una carta para voltearla; mantenla presionada para ver la ficha.</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { gap: 10 },
  sorts: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  sortLabel: { color: '#9DB8A8', fontSize: 12 },
  chip: {
    minHeight: MIN_TOUCH,
    paddingHorizontal: 12,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#1D3A29',
    backgroundColor: '#0E2217',
    justifyContent: 'center',
  },
  chipOn: { borderColor: '#2BD46B', backgroundColor: '#2BD46B' },
  chipText: { color: '#EAF5EE', fontSize: 12, fontWeight: '700' },
  chipTextOn: { color: '#06120C', fontWeight: '900' },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10, justifyContent: 'flex-start' },
  hint: { color: '#9DB8A8', fontSize: 12 },
});
