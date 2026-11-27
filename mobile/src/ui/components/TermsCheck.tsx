// Aceptación de Términos y Privacidad (Sprint 27): casilla clara, enlaces a los textos y error visible.

import { Pressable, StyleSheet, Text, View } from 'react-native';

import { colors, font, MIN_TOUCH, radius, space } from '../theme';

interface Props {
  checked: boolean;
  error?: string;
  onToggle: () => void;
  onOpen: (doc: 'terms' | 'privacy') => void;
}

export function TermsCheck({ checked, error, onToggle, onOpen }: Props) {
  return (
    <View style={styles.wrap}>
      <Pressable
        onPress={onToggle}
        accessibilityRole="checkbox"
        accessibilityState={{ checked }}
        accessibilityLabel="Acepto los Términos y la Política de privacidad y declaro que soy mayor de 18"
        style={styles.row}
      >
        <View style={[styles.box, checked ? styles.boxOn : null]}>
          <Text style={styles.tick}>{checked ? '✓' : ''}</Text>
        </View>
        <Text style={styles.text}>
          Acepto los Términos y la Política de privacidad, autorizo el tratamiento de mis datos y declaro que
          soy mayor de 18.
        </Text>
      </Pressable>
      <View style={styles.links}>
        <Pressable onPress={() => onOpen('terms')} accessibilityRole="link" style={styles.link}>
          <Text style={styles.linkText}>Leer los Términos</Text>
        </Pressable>
        <Pressable onPress={() => onOpen('privacy')} accessibilityRole="link" style={styles.link}>
          <Text style={styles.linkText}>Leer la Privacidad</Text>
        </Pressable>
      </View>
      {error ? (
        <Text style={styles.error} accessibilityLiveRegion="assertive">
          {error}
        </Text>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { gap: space.sm },
  row: { flexDirection: 'row', gap: space.sm, alignItems: 'flex-start', minHeight: MIN_TOUCH },
  box: {
    width: 26,
    height: 26,
    borderRadius: radius.sm,
    borderWidth: 2,
    borderColor: colors.textMuted,
    alignItems: 'center',
    justifyContent: 'center',
  },
  boxOn: { backgroundColor: colors.accent, borderColor: colors.accent },
  tick: { color: colors.accentText, fontSize: 16, fontWeight: '900' },
  text: { flex: 1, color: colors.text, fontSize: font.small },
  links: { flexDirection: 'row', gap: space.md },
  link: { minHeight: MIN_TOUCH, justifyContent: 'center' },
  linkText: { color: colors.accent, fontSize: font.small, fontWeight: '700' },
  error: { color: colors.danger, fontSize: font.small },
});
