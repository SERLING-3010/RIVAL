import { useState } from 'react';
import type { KeyboardTypeOptions } from 'react-native';
import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

import { colors, font, MIN_TOUCH, radius, space } from '../theme';

interface Props {
  label: string;
  value: string;
  onChangeText: (value: string) => void;
  error?: string;
  hint?: string;
  secure?: boolean;
  keyboardType?: KeyboardTypeOptions;
  placeholder?: string;
}

export function TextField({
  label,
  value,
  onChangeText,
  error,
  hint,
  secure = false,
  keyboardType,
  placeholder,
}: Props) {
  const [hidden, setHidden] = useState(secure);
  return (
    <View style={styles.wrapper}>
      <Text style={styles.label}>{label}</Text>
      <View style={styles.row}>
        <TextInput
          value={value}
          onChangeText={onChangeText}
          secureTextEntry={hidden}
          keyboardType={keyboardType}
          placeholder={placeholder}
          placeholderTextColor={colors.disabled}
          autoCapitalize={keyboardType === 'email-address' || secure ? 'none' : 'sentences'}
          autoCorrect={false}
          accessibilityLabel={label}
          accessibilityHint={error ?? hint}
          style={[styles.input, error ? styles.inputError : null]}
        />
        {secure ? (
          <Pressable
            onPress={() => setHidden((h) => !h)}
            accessibilityRole="button"
            accessibilityLabel={hidden ? 'Mostrar contraseña' : 'Ocultar contraseña'}
            style={styles.toggle}
          >
            <Text style={styles.toggleText}>{hidden ? 'Mostrar' : 'Ocultar'}</Text>
          </Pressable>
        ) : null}
      </View>
      {error ? (
        <Text style={styles.error} accessibilityLiveRegion="polite">
          {error}
        </Text>
      ) : hint ? (
        <Text style={styles.hint}>{hint}</Text>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { gap: space.xs },
  label: { color: colors.text, fontSize: font.small, fontWeight: '600' },
  row: { flexDirection: 'row', alignItems: 'center', gap: space.sm },
  input: {
    flex: 1,
    minHeight: MIN_TOUCH,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.sm,
    paddingHorizontal: space.md,
    backgroundColor: colors.surface,
    color: colors.text,
    fontSize: font.body,
  },
  inputError: { borderColor: colors.danger },
  toggle: { minHeight: MIN_TOUCH, justifyContent: 'center', paddingHorizontal: space.sm },
  toggleText: { color: colors.accent, fontSize: font.small },
  error: { color: colors.danger, fontSize: font.small },
  hint: { color: colors.textMuted, fontSize: font.small },
});
