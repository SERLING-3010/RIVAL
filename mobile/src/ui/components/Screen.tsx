import type { ReactNode } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { colors, font, MIN_TOUCH, space } from '../theme';

interface Props {
  title: string;
  onBack?: () => void;
  tone?: 'light' | 'dark'; // oscuro: pantallas del modo juego del manager (Sprint 20)
  children: ReactNode;
}

export function Screen({ title, onBack, tone = 'light', children }: Props) {
  const insets = useSafeAreaInsets();
  const dark = tone === 'dark';
  return (
    <View
      style={[
        styles.root,
        dark ? styles.darkRoot : null,
        { paddingTop: insets.top, paddingBottom: insets.bottom },
      ]}
    >
      <View style={styles.header}>
        {onBack ? (
          <Pressable
            onPress={onBack}
            accessibilityRole="button"
            accessibilityLabel="Volver"
            style={styles.back}
          >
            <Text style={[styles.backText, dark ? styles.darkBack : null]}>‹ Volver</Text>
          </Pressable>
        ) : null}
        <Text style={[styles.title, dark ? styles.darkTitle : null]} accessibilityRole="header">
          {title}
        </Text>
      </View>
      {/* El teclado no debe tapar el campo que se escribe (visto en iPhone): iOS ajusta el
          desplazamiento y lleva el campo activo a la vista; Android redimensiona la pantalla. */}
      <ScrollView
        contentContainerStyle={styles.content}
        keyboardShouldPersistTaps="handled"
        keyboardDismissMode="interactive"
        automaticallyAdjustKeyboardInsets
      >
        {children}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.background },
  darkRoot: { backgroundColor: '#06120C' },
  darkBack: { color: '#2BD46B' },
  darkTitle: { color: '#EAF5EE' },
  header: { paddingHorizontal: space.md, paddingTop: space.sm, paddingBottom: space.sm },
  back: { minHeight: MIN_TOUCH, justifyContent: 'center', alignSelf: 'flex-start' },
  backText: { color: colors.accent, fontSize: font.body },
  title: { color: colors.text, fontSize: font.title, fontWeight: '700' },
  content: { padding: space.md, gap: space.md },
});
