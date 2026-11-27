// Armar el escudo del equipo (Sprint 23): forma, color de fondo, color del detalle y símbolo.

import { useEffect, useState } from 'react';
import { Modal, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import type { Crest } from '../../domain/teamLook';
import {
  CREST_COLORS,
  CREST_SHAPES,
  CREST_SYMBOLS,
  DEFAULT_CREST,
  encodeCrest,
  SHAPE_LABEL,
  SYMBOL_LABEL,
} from '../../domain/teamLook';
import { MIN_TOUCH } from '../theme';
import { PrimaryButton } from './PrimaryButton';
import { TeamCrest } from './TeamCrest';

interface Props {
  visible: boolean;
  initial: Crest | null;
  teamName: string;
  busy: boolean;
  onSave: (crest: string | null) => void;
  onClose: () => void;
}

export function CrestEditor({ visible, initial, teamName, busy, onSave, onClose }: Props) {
  const [draft, setDraft] = useState<Crest>(initial ?? DEFAULT_CREST);
  useEffect(() => setDraft(initial ?? DEFAULT_CREST), [initial, visible]);
  const set = (part: Partial<Crest>) => setDraft((d) => ({ ...d, ...part }));
  const chip = (on: boolean) => [styles.chip, on ? styles.chipOn : null];
  const colors = (key: 'primary' | 'secondary', label: string) => (
    <>
      <Text style={styles.label}>{label}</Text>
      <View style={styles.row}>
        {CREST_COLORS.map((c) => (
          <Pressable
            key={c}
            onPress={() => set({ [key]: c })}
            accessibilityRole="radio"
            accessibilityLabel={`${label}: ${c}`}
            accessibilityState={{ checked: draft[key] === c }}
            style={[styles.color, { backgroundColor: c }, draft[key] === c ? styles.colorOn : null]}
          />
        ))}
      </View>
    </>
  );
  return (
    <Modal visible={visible} transparent animationType="slide" onRequestClose={onClose}>
      <Pressable style={styles.backdrop} onPress={onClose} accessibilityLabel="Cerrar" />
      <ScrollView style={styles.sheet} contentContainerStyle={styles.content}>
        <Text style={styles.title}>Escudo del equipo</Text>
        <View style={styles.preview}>
          <TeamCrest crest={draft} teamName={teamName} size={80} />
        </View>
        <Text style={styles.label}>Forma</Text>
        <View style={styles.row}>
          {CREST_SHAPES.map((s) => (
            <Pressable key={s} onPress={() => set({ shape: s })} style={chip(draft.shape === s)}>
              <Text style={styles.chipText}>{SHAPE_LABEL[s]}</Text>
            </Pressable>
          ))}
        </View>
        {colors('primary', 'Color de fondo')}
        {colors('secondary', 'Color del detalle')}
        <Text style={styles.label}>Símbolo</Text>
        <View style={styles.row}>
          {CREST_SYMBOLS.map((s) => (
            <Pressable key={s} onPress={() => set({ symbol: s })} style={chip(draft.symbol === s)}>
              <Text style={styles.chipText}>{SYMBOL_LABEL[s]}</Text>
            </Pressable>
          ))}
        </View>
        {draft.primary === draft.secondary ? (
          <Text style={styles.warn}>Usa dos colores distintos para que el escudo se vea.</Text>
        ) : null}
        <PrimaryButton
          label="Guardar escudo"
          disabled={busy || draft.primary === draft.secondary}
          onPress={() => onSave(encodeCrest(draft))}
        />
        <PrimaryButton
          label="Volver al predeterminado"
          variant="secondary"
          disabled={busy}
          onPress={() => onSave(null)}
        />
      </ScrollView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)' },
  sheet: { maxHeight: '80%', backgroundColor: '#0E2217', borderTopLeftRadius: 20, borderTopRightRadius: 20 },
  content: { padding: 20, gap: 10 },
  title: { color: '#EAF5EE', fontSize: 20, fontWeight: '900' },
  preview: { alignItems: 'center', paddingVertical: 6 },
  label: { color: '#9DB8A8', fontSize: 13, fontWeight: '700' },
  row: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  chip: {
    minHeight: MIN_TOUCH,
    paddingHorizontal: 14,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#1D3A29',
    justifyContent: 'center',
  },
  chipOn: { borderColor: '#2BD46B', backgroundColor: '#123A25' },
  chipText: { color: '#EAF5EE', fontSize: 14, fontWeight: '700' },
  color: { width: MIN_TOUCH, height: MIN_TOUCH, borderRadius: 22, borderWidth: 2, borderColor: '#1D3A29' },
  colorOn: { borderColor: '#2BD46B', borderWidth: 4 },
  warn: { color: '#FFB48A', fontSize: 13 },
});
