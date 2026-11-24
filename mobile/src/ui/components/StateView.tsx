// Pinta los 7 estados de una vista. Solo el estado "success" muestra el contenido real.

import type { ReactNode } from 'react';
import { ActivityIndicator, StyleSheet, Text, View } from 'react-native';

import type { ViewState } from '../../domain/viewState';
import { colors, font, radius, space } from '../theme';
import { PrimaryButton } from './PrimaryButton';

interface Props<T> {
  state: ViewState<T>;
  onRetry?: () => void;
  emptyAction?: { label: string; onPress: () => void };
  children: (data: T) => ReactNode;
}

const TITLES = {
  empty: 'Nada por aquí todavía',
  error: 'No pudimos cargar esto',
  offline: 'Sin conexión',
  conflict: 'Hay un cambio que revisar',
  approvalGate: 'Necesita aprobación',
} as const;

export function StateView<T>({ state, onRetry, emptyAction, children }: Props<T>) {
  if (state.kind === 'success') {
    return <>{children(state.data)}</>;
  }
  if (state.kind === 'loading') {
    return (
      <View style={styles.box} accessibilityLabel="Cargando" accessibilityLiveRegion="polite">
        <ActivityIndicator color={colors.accent} />
        <View style={styles.skeleton} />
        <View style={[styles.skeleton, styles.skeletonShort]} />
      </View>
    );
  }
  const tone =
    state.kind === 'error' ? colors.danger : state.kind === 'empty' ? colors.textMuted : colors.warning;
  return (
    <View style={[styles.box, { borderLeftColor: tone }]} accessibilityLiveRegion="polite">
      <Text style={styles.title}>{TITLES[state.kind]}</Text>
      <Text style={styles.message}>{state.message}</Text>
      {state.kind === 'error' && state.correlationId ? (
        <Text style={styles.code}>Código para soporte: {state.correlationId.slice(0, 12)}</Text>
      ) : null}
      {state.kind === 'empty' && emptyAction ? (
        <PrimaryButton label={emptyAction.label} onPress={emptyAction.onPress} />
      ) : null}
      {onRetry && state.kind !== 'empty' && state.kind !== 'approvalGate' ? (
        <PrimaryButton label="Reintentar" variant="secondary" onPress={onRetry} />
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  box: {
    gap: space.sm,
    padding: space.md,
    borderRadius: radius.md,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderLeftWidth: 4,
    borderLeftColor: colors.border,
  },
  title: { color: colors.text, fontSize: font.heading, fontWeight: '700' },
  message: { color: colors.textMuted, fontSize: font.body },
  code: { color: colors.textMuted, fontSize: font.small },
  skeleton: { height: 16, borderRadius: radius.sm, backgroundColor: colors.border },
  skeletonShort: { width: '60%' },
});
