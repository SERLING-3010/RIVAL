import type { ReactNode } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { colors, font, MIN_TOUCH, space } from '../theme';

interface Props {
  title: string;
  onBack?: () => void;
  children: ReactNode;
}

export function Screen({ title, onBack, children }: Props) {
  const insets = useSafeAreaInsets();
  return (
    <View style={[styles.root, { paddingTop: insets.top, paddingBottom: insets.bottom }]}>
      <View style={styles.header}>
        {onBack ? (
          <Pressable
            onPress={onBack}
            accessibilityRole="button"
            accessibilityLabel="Volver"
            style={styles.back}
          >
            <Text style={styles.backText}>‹ Volver</Text>
          </Pressable>
        ) : null}
        <Text style={styles.title} accessibilityRole="header">
          {title}
        </Text>
      </View>
      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
        {children}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.background },
  header: { paddingHorizontal: space.md, paddingTop: space.sm, paddingBottom: space.sm },
  back: { minHeight: MIN_TOUCH, justifyContent: 'center', alignSelf: 'flex-start' },
  backText: { color: colors.accent, fontSize: font.body },
  title: { color: colors.text, fontSize: font.title, fontWeight: '700' },
  content: { padding: space.md, gap: space.md },
});
