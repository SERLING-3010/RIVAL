// Términos o Política de privacidad (Sprint 27). Texto en borrador hasta que lo revise un abogado.

import { StyleSheet, Text, View } from 'react-native';

import { PRIVACY } from '../../domain/legalPrivacy';
import { TERMS, TERMS_VERSION } from '../../domain/legalTerms';
import { Screen } from '../components/Screen';
import { colors, font, space } from '../theme';

export function LegalScreen({ doc, onBack }: { doc: 'terms' | 'privacy'; onBack: () => void }) {
  const sections = doc === 'terms' ? TERMS : PRIVACY;
  return (
    <Screen title={doc === 'terms' ? 'Términos de uso' : 'Política de privacidad'} onBack={onBack}>
      <Text style={styles.meta}>Versión {TERMS_VERSION} · borrador para el piloto</Text>
      {sections.map((s) => (
        <View key={s.title} style={styles.section}>
          <Text style={styles.title} accessibilityRole="header">
            {s.title}
          </Text>
          <Text style={styles.body}>{s.body}</Text>
        </View>
      ))}
    </Screen>
  );
}

const styles = StyleSheet.create({
  meta: { color: colors.textMuted, fontSize: font.small },
  section: { gap: space.xs },
  title: { color: colors.text, fontSize: font.heading, fontWeight: '700' },
  body: { color: colors.text, fontSize: font.body, lineHeight: 22 },
});
