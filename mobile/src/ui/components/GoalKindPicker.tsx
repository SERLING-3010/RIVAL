// Tipos de gol de un jugador en la planilla (Sprint 23): toca un tipo para sumarlo y ✕ para quitarlo.

import { Pressable, StyleSheet, Text, View } from 'react-native';

import type { GoalKind } from '../../domain/goalKinds';
import { GOAL_KIND_LABEL, GOAL_KINDS } from '../../domain/goalKinds';
import { colors, font, MIN_TOUCH, radius, space } from '../theme';

interface Props {
  name: string;
  goals: number;
  marked: GoalKind[];
  onAdd: (kind: GoalKind) => void;
  onRemove: (index: number) => void;
}

export function GoalKindPicker({ name, goals, marked, onAdd, onRemove }: Props) {
  if (goals <= 0) return null;
  const full = marked.length >= goals;
  return (
    <View style={styles.wrap}>
      <Text style={styles.label}>
        ¿Algún gol especial? ({marked.length} de {goals}). El rival lo confirma.
      </Text>
      <View style={styles.row}>
        {GOAL_KINDS.map((kind) => (
          <Pressable
            key={kind}
            disabled={full}
            onPress={() => onAdd(kind)}
            accessibilityRole="button"
            accessibilityLabel={`Sumar un gol de tipo ${GOAL_KIND_LABEL[kind]} a ${name}`}
            accessibilityState={{ disabled: full }}
            style={[styles.chip, full ? styles.off : null]}
          >
            <Text style={styles.chipText}>+ {GOAL_KIND_LABEL[kind]}</Text>
          </Pressable>
        ))}
      </View>
      {marked.length > 0 ? (
        <View style={styles.row}>
          {marked.map((kind, i) => (
            <Pressable
              key={`${kind}-${i}`}
              onPress={() => onRemove(i)}
              accessibilityRole="button"
              accessibilityLabel={`Quitar ${GOAL_KIND_LABEL[kind]} de ${name}`}
              style={[styles.chip, styles.marked]}
            >
              <Text style={styles.markedText}>{GOAL_KIND_LABEL[kind]} ✕</Text>
            </Pressable>
          ))}
        </View>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { gap: space.sm },
  label: { color: colors.textMuted, fontSize: font.small },
  row: { flexDirection: 'row', flexWrap: 'wrap', gap: space.sm },
  chip: {
    minHeight: MIN_TOUCH,
    paddingHorizontal: space.md,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    justifyContent: 'center',
  },
  off: { opacity: 0.4 },
  chipText: { color: colors.text, fontSize: font.small, fontWeight: '600' },
  marked: { backgroundColor: colors.accent, borderColor: colors.accent },
  markedText: { color: colors.accentText, fontSize: font.small, fontWeight: '700' },
});
