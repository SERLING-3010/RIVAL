// Marcador del partido: lo que reportó cada equipo y, si corresponde, el formulario para reportar.

import { useState } from 'react';
import { StyleSheet, Text } from 'react-native';

import type { Contract } from '../../domain/contractModels';
import { RESULT_STATUS_LABEL } from '../../domain/contractRules';
import { colors, font } from '../theme';
import { Card } from './Card';
import { PrimaryButton } from './PrimaryButton';
import { TextField } from './TextField';

interface Props {
  contract: Contract;
  canReport: boolean;
  busy: boolean;
  onReport: (hostScore: number, guestScore: number) => void;
}

const score = (text: string): number | null => (/^\d{1,3}$/.test(text.trim()) ? Number(text) : null);

export function ResultPanel({ contract, canReport, busy, onReport }: Props) {
  const [host, setHost] = useState('');
  const [guest, setGuest] = useState('');
  const [error, setError] = useState<string | null>(null);
  const result = contract.result;
  if (!result && !canReport) return null;
  const name = (side: string) => (side === 'HOST' ? contract.host.name : contract.guest.name);
  const submit = () => {
    const h = score(host);
    const g = score(guest);
    if (h === null || g === null) {
      setError('Escribe el marcador de cada equipo con números de 0 a 999.');
      return;
    }
    setError(null);
    onReport(h, g);
  };
  const confirmed = result?.status === 'CONFIRMED';
  return (
    <Card
      title={confirmed ? `Resultado: ${result?.host_score} – ${result?.guest_score}` : 'Resultado'}
      badge={result ? RESULT_STATUS_LABEL[result.status] : undefined}
    >
      {(result?.reports ?? []).map((r) => (
        <Text key={r.side} style={styles.line}>
          {name(r.side)} reportó: {contract.host.name} {r.host_score} – {r.guest_score} {contract.guest.name}
        </Text>
      ))}
      {canReport ? (
        <>
          <TextField
            label={`Goles de ${contract.host.name}`}
            keyboardType="number-pad"
            value={host}
            onChangeText={setHost}
          />
          <TextField
            label={`Goles de ${contract.guest.name}`}
            keyboardType="number-pad"
            value={guest}
            onChangeText={setGuest}
          />
          {error ? <Text style={styles.error}>{error}</Text> : null}
          <PrimaryButton label="Reportar marcador" disabled={busy} onPress={submit} />
          <Text style={styles.meta}>
            Vale cuando el rival reporta el mismo marcador; si no coincide, queda en disputa.
          </Text>
        </>
      ) : null}
    </Card>
  );
}

const styles = StyleSheet.create({
  line: { color: colors.text, fontSize: font.small },
  meta: { color: colors.textMuted, fontSize: font.small },
  error: { color: colors.danger, fontSize: font.body },
});
