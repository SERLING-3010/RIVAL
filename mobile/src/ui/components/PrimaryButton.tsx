import { ActivityIndicator, Pressable, StyleSheet, Text } from 'react-native';

import { colors, font, MIN_TOUCH, radius, space } from '../theme';

interface Props {
  label: string;
  onPress: () => void;
  loading?: boolean;
  disabled?: boolean;
  variant?: 'primary' | 'secondary' | 'danger';
}

export function PrimaryButton({
  label,
  onPress,
  loading = false,
  disabled = false,
  variant = 'primary',
}: Props) {
  const inactive = disabled || loading;
  return (
    <Pressable
      onPress={onPress}
      disabled={inactive}
      accessibilityRole="button"
      accessibilityLabel={label}
      accessibilityState={{ disabled: inactive, busy: loading }}
      style={({ pressed }) => [
        styles.base,
        variant === 'primary' && styles.primary,
        variant === 'secondary' && styles.secondary,
        variant === 'danger' && styles.danger,
        inactive && styles.inactive,
        pressed && !inactive && styles.pressed,
      ]}
    >
      {loading ? (
        <ActivityIndicator color={variant === 'secondary' ? colors.accent : colors.accentText} />
      ) : (
        <Text style={[styles.label, variant === 'secondary' && styles.secondaryLabel]}>{label}</Text>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  base: {
    minHeight: MIN_TOUCH,
    borderRadius: radius.sm,
    paddingHorizontal: space.md,
    alignItems: 'center',
    justifyContent: 'center',
  },
  primary: { backgroundColor: colors.accent },
  secondary: { backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.accent },
  danger: { backgroundColor: colors.danger },
  inactive: { backgroundColor: colors.disabled, borderColor: colors.disabled },
  pressed: { opacity: 0.85 },
  label: { color: colors.accentText, fontSize: font.body, fontWeight: '600' },
  secondaryLabel: { color: colors.accent },
});
