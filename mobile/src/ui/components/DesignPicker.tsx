// Elegir el diseño del cuadro de la media (Sprint 23): automático, la básica o una especial ya ganada.

import { Modal, Pressable, StyleSheet, Text, View } from 'react-native';

import type { BaseTier, CardTier } from '../../domain/cardTiers';
import { TIERS } from '../../domain/cardTiers';
import { BASIC } from '../../domain/teamLook';
import { MIN_TOUCH } from '../theme';
import { TierFoil } from './TierFoil';

interface Props {
  visible: boolean;
  basic: BaseTier;
  available: string[];
  chosen: string | null;
  onPick: (choice: string | null) => void;
  onClose: () => void;
}

export function DesignPicker({ visible, basic, available, chosen, onPick, onClose }: Props) {
  const best = available[available.length - 1];
  const autoTier = (best === undefined || best === BASIC ? basic : best) as CardTier;
  const options: { key: string | null; tier: CardTier; label: string }[] = [
    { key: null, tier: autoTier, label: 'Automático: la mejor' },
    ...available.map((code) => {
      const tier = (code === BASIC ? basic : code) as CardTier;
      return { key: code, tier, label: code === BASIC ? `Básica: ${TIERS[basic].label}` : TIERS[tier].label };
    }),
  ];
  return (
    <Modal visible={visible} transparent animationType="slide" onRequestClose={onClose}>
      <Pressable style={styles.backdrop} onPress={onClose} accessibilityLabel="Cerrar" />
      <View style={styles.sheet}>
        <Text style={styles.title}>Diseño del equipo</Text>
        <Text style={styles.meta}>
          Solo los que el equipo ya ganó. Lo ven todos los que miran la plantilla.
        </Text>
        {options.map((o) => {
          const on = o.key === chosen;
          return (
            <Pressable
              key={o.key ?? 'auto'}
              onPress={() => onPick(o.key)}
              accessibilityRole="radio"
              accessibilityState={{ checked: on }}
              style={[styles.row, on ? styles.rowOn : null]}
            >
              <View style={styles.swatch}>
                <TierFoil tier={o.tier} radius={8} frameWidth={1} />
              </View>
              <Text style={styles.label}>{o.label}</Text>
              <Text style={styles.check}>{on ? '✓' : ''}</Text>
            </Pressable>
          );
        })}
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)' },
  sheet: {
    backgroundColor: '#0E2217',
    padding: 20,
    gap: 10,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
  },
  title: { color: '#EAF5EE', fontSize: 20, fontWeight: '900' },
  meta: { color: '#9DB8A8', fontSize: 13 },
  row: {
    minHeight: MIN_TOUCH + 8,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    paddingHorizontal: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#1D3A29',
  },
  rowOn: { borderColor: '#2BD46B', backgroundColor: '#123A25' },
  swatch: { width: 34, height: 40 },
  label: { flex: 1, color: '#EAF5EE', fontSize: 15, fontWeight: '700' },
  check: { color: '#2BD46B', fontSize: 18, fontWeight: '900' },
});
