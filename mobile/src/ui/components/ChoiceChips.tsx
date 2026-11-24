import { Pressable, StyleSheet, Text, View } from 'react-native';

import { colors, font, MIN_TOUCH, radius, space } from '../theme';

export interface Choice {
  value: string;
  label: string;
}

interface Props {
  label: string;
  choices: Choice[];
  selected: string[];
  onToggle: (value: string) => void;
  error?: string;
}

// Selección con fichas: el estado elegido se marca con borde, peso y "✓", no solo con color.
export function ChoiceChips({ label, choices, selected, onToggle, error }: Props) {
  return (
    <View style={styles.wrapper} accessibilityRole="radiogroup" accessibilityLabel={label}>
      <Text style={styles.label}>{label}</Text>
      <View style={styles.row}>
        {choices.map((choice) => {
          const isOn = selected.includes(choice.value);
          return (
            <Pressable
              key={choice.value}
              onPress={() => onToggle(choice.value)}
              accessibilityRole="checkbox"
              accessibilityState={{ checked: isOn }}
              accessibilityLabel={choice.label}
              style={[styles.chip, isOn && styles.chipOn]}
            >
              <Text style={[styles.chipText, isOn && styles.chipTextOn]}>
                {isOn ? `✓ ${choice.label}` : choice.label}
              </Text>
            </Pressable>
          );
        })}
      </View>
      {error ? <Text style={styles.error}>{error}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { gap: space.xs },
  label: { color: colors.text, fontSize: font.small, fontWeight: '600' },
  row: { flexDirection: 'row', flexWrap: 'wrap', gap: space.sm },
  chip: {
    minHeight: MIN_TOUCH,
    justifyContent: 'center',
    paddingHorizontal: space.md,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surface,
  },
  chipOn: { borderColor: colors.accent, borderWidth: 2 },
  chipText: { color: colors.text, fontSize: font.small },
  chipTextOn: { color: colors.accent, fontWeight: '700' },
  error: { color: colors.danger, fontSize: font.small },
});
