// Ventana de traspasos de la liga: todos la ven; el organizador la fija o la quita.

import { useState } from 'react';
import { StyleSheet, Text } from 'react-native';

import type { TransferWindowController } from '../../controllers/useTransferWindow';
import { formatLocal, isoToLocalText } from '../../domain/dateTime';
import { parseWindow, windowText } from '../../domain/loanModels';
import { colors, font } from '../theme';
import { Card } from './Card';
import { PrimaryButton } from './PrimaryButton';
import { TextField } from './TextField';

interface Props {
  start: string | null;
  end: string | null;
  canEdit: boolean;
  controller: TransferWindowController;
  now?: Date;
}

export function TransferWindowCard({ start, end, canEdit, controller, now = new Date() }: Props) {
  const [startText, setStartText] = useState(start ? isoToLocalText(start) : '');
  const [endText, setEndText] = useState(end ? isoToLocalText(end) : '');
  const [error, setError] = useState<string | undefined>(undefined);
  const busy = controller.action.busy;
  const save = () => {
    const form = parseWindow(startText, endText);
    if (!form.ok) {
      setError(form.error);
      return;
    }
    setError(undefined);
    void controller.handleSave(form.start, form.end);
  };
  return (
    <Card title="Ventana de traspasos" subtitle={windowText(start, end, now, formatLocal)}>
      <Text style={styles.meta}>
        Fuera de la ventana no se ofertan ni se cierran traspasos con equipos de la liga.
      </Text>
      {canEdit ? (
        <>
          <TextField label="Abre (dd/mm/aaaa hh:mm)" value={startText} onChangeText={setStartText} />
          <TextField
            label="Cierra (dd/mm/aaaa hh:mm)"
            value={endText}
            onChangeText={setEndText}
            error={error}
          />
          <PrimaryButton label="Guardar ventana" disabled={busy} onPress={save} />
          {start !== null ? (
            <PrimaryButton
              label="Quitar ventana"
              variant="secondary"
              disabled={busy}
              onPress={() => void controller.handleClear()}
            />
          ) : null}
        </>
      ) : null}
      {controller.action.message ? (
        <Text style={styles.meta} accessibilityLiveRegion="polite">
          {controller.action.message}
        </Text>
      ) : null}
    </Card>
  );
}

const styles = StyleSheet.create({
  meta: { color: colors.textMuted, fontSize: font.small },
});
