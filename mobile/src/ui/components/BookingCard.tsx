// Cancha del partido en el contrato: reserva actual, y botones para reservar o cancelar.

import { StyleSheet, Text } from 'react-native';

import type { Contract } from '../../domain/contractModels';
import { formatLocal } from '../../domain/dateTime';
import { bookingActions, BOOKING_STATUS_LABEL } from '../../domain/venueRules';
import { colors, font } from '../theme';
import { Card } from './Card';
import { PrimaryButton } from './PrimaryButton';

interface Props {
  contract: Contract;
  busy: boolean;
  onBook: () => void;
  onCancel: (bookingId: number) => void;
}

export function BookingCard({ contract, busy, onBook, onCancel }: Props) {
  const can = bookingActions(contract);
  const booking = contract.booking;
  if (!booking && !can.canBook) return null;
  return (
    <Card title="Cancha" badge={booking ? BOOKING_STATUS_LABEL[booking.status] : undefined}>
      {booking ? (
        <>
          <Text style={styles.line}>
            {booking.venue_name} · {booking.slot.court_name}
          </Text>
          <Text style={styles.line}>{booking.address}</Text>
          <Text style={styles.meta}>
            Franja: {formatLocal(booking.slot.starts_at)} – {formatLocal(booking.slot.ends_at)}
          </Text>
        </>
      ) : null}
      {can.canBook ? <PrimaryButton label="Reservar cancha" disabled={busy} onPress={onBook} /> : null}
      {can.canCancelBooking && booking ? (
        <PrimaryButton
          label="Cancelar reserva"
          variant="secondary"
          disabled={busy}
          onPress={() => onCancel(booking.id)}
        />
      ) : null}
      <Text style={styles.meta}>La cancha se paga en el establecimiento, como lo acuerden.</Text>
    </Card>
  );
}

const styles = StyleSheet.create({
  line: { color: colors.text, fontSize: font.small },
  meta: { color: colors.textMuted, fontSize: font.small },
});
