import type { ReactNode } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { colors, font, radius, space } from '../theme';

interface Props {
  title: string;
  subtitle?: string;
  badge?: string;
  onPress?: () => void;
  children?: ReactNode;
}

export function Card({ title, subtitle, badge, onPress, children }: Props) {
  const body = (
    <>
      <View style={styles.headerRow}>
        <Text style={styles.title}>{title}</Text>
        {badge ? <Text style={styles.badge}>{badge}</Text> : null}
      </View>
      {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
      {children}
    </>
  );
  if (!onPress) {
    return <View style={styles.card}>{body}</View>;
  }
  return (
    <Pressable
      onPress={onPress}
      accessibilityRole="button"
      accessibilityLabel={subtitle ? `${title}. ${subtitle}` : title}
      style={({ pressed }) => [styles.card, pressed && styles.pressed]}
    >
      {body}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    gap: space.sm,
    padding: space.md,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surface,
  },
  pressed: { opacity: 0.85 },
  headerRow: { flexDirection: 'row', justifyContent: 'space-between', gap: space.sm },
  title: { flex: 1, color: colors.text, fontSize: font.heading, fontWeight: '600' },
  subtitle: { color: colors.textMuted, fontSize: font.small },
  badge: {
    color: colors.accent,
    fontSize: font.small,
    fontWeight: '700',
    borderWidth: 1,
    borderColor: colors.accent,
    borderRadius: radius.sm,
    paddingHorizontal: space.sm,
  },
});
