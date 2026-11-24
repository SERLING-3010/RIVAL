// Herramientas del dueño: agregar canchas, publicar franjas y decidir reservas.

import { useState } from 'react';
import { StyleSheet, Text } from 'react-native';

import type { VenueController } from '../../controllers/useVenues';
import { formatLocal } from '../../domain/dateTime';
import type { Sport } from '../../domain/models';
import type { VenueDetail } from '../../domain/venueModels';
import { colors, font } from '../theme';
import { Card } from './Card';
import { ChoiceChips } from './ChoiceChips';
import { PrimaryButton } from './PrimaryButton';
import { TextField } from './TextField';

interface Props {
  detail: VenueDetail;
  sports: Sport[];
  controller: VenueController;
}

export function VenueOwnerPanel({ detail, sports, controller }: Props) {
  const busy = controller.action.busy;
  const [court, setCourt] = useState({ name: '', sport: sports[0]?.code ?? '', surface: '' });
  const [slot, setSlot] = useState({ courtId: detail.courts[0]?.id ?? 0, start: '', minutes: '90' });
  const [slotError, setSlotError] = useState<string | null>(null);
  const publish = async () =>
    setSlotError(await controller.handleAddSlot(slot.courtId, slot.start, slot.minutes));
  return (
    <>
      <Card title={`Reservas por confirmar (${detail.pending_bookings.length})`}>
        {detail.pending_bookings.map((b) => (
          <Card
            key={b.id}
            title={`${b.host_name} vs ${b.guest_name}`}
            subtitle={`${b.slot.court_name} · ${formatLocal(b.slot.starts_at)}`}
          >
            <PrimaryButton
              label="Confirmar"
              disabled={busy}
              onPress={() => void controller.handleDecide(b.id, 'confirm')}
            />
            <PrimaryButton
              label="Rechazar"
              variant="secondary"
              disabled={busy}
              onPress={() => void controller.handleDecide(b.id, 'reject')}
            />
          </Card>
        ))}
      </Card>
      <Card title={`Reservas confirmadas (${detail.confirmed_bookings.length})`}>
        {detail.confirmed_bookings.map((b) => (
          <Text key={b.id} style={styles.line}>
            {formatLocal(b.slot.starts_at)} · {b.slot.court_name} · {b.host_name} vs {b.guest_name}
          </Text>
        ))}
      </Card>
      {detail.courts.length > 0 ? (
        <Card title="Publicar franja">
          <ChoiceChips
            label="Cancha"
            selected={[String(slot.courtId)]}
            choices={detail.courts.map((c) => ({ value: String(c.id), label: c.name }))}
            onToggle={(v) => setSlot((s) => ({ ...s, courtId: Number(v) }))}
          />
          <TextField
            label="Inicio (dd/mm/aaaa hh:mm)"
            value={slot.start}
            onChangeText={(v) => setSlot((s) => ({ ...s, start: v }))}
          />
          <TextField
            label="Duración (minutos)"
            keyboardType="number-pad"
            value={slot.minutes}
            onChangeText={(v) => setSlot((s) => ({ ...s, minutes: v }))}
          />
          {slotError ? <Text style={styles.error}>{slotError}</Text> : null}
          <PrimaryButton label="Publicar franja" disabled={busy} onPress={() => void publish()} />
        </Card>
      ) : null}
      <Card title="Agregar cancha">
        <TextField
          label="Nombre de la cancha"
          value={court.name}
          onChangeText={(v) => setCourt((c) => ({ ...c, name: v }))}
        />
        <ChoiceChips
          label="Deporte"
          selected={[court.sport]}
          choices={sports.map((s) => ({ value: s.code, label: s.name }))}
          onToggle={(v) => setCourt((c) => ({ ...c, sport: v }))}
        />
        <TextField
          label="Superficie (opcional)"
          value={court.surface}
          onChangeText={(v) => setCourt((c) => ({ ...c, surface: v }))}
        />
        <PrimaryButton
          label="Agregar cancha"
          disabled={busy || court.name.trim() === ''}
          onPress={() => void controller.handleAddCourt(court.name, court.sport, court.surface)}
        />
      </Card>
    </>
  );
}

const styles = StyleSheet.create({
  line: { color: colors.text, fontSize: font.small },
  error: { color: colors.danger, fontSize: font.body },
});
