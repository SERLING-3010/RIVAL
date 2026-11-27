// Reglas locales de canchas y reservas. El backend vuelve a validar todo.

import type { Contract } from './contractModels';
import { parseLocalDateTime } from './dateTime.ts';
import type { BookingStatus, Slot } from './venueModels';

export const BOOKING_STATUS_LABEL: Record<BookingStatus, string> = {
  PENDING: 'Esperando confirmación del establecimiento',
  CONFIRMED: 'Cancha confirmada',
  REJECTED: 'El establecimiento rechazó la reserva',
  CANCELLED: 'Reserva cancelada',
};

/** "80000.00" → "$80.000"; "80000.50" → "$80.000,50". Trabaja sobre el texto: nunca pasa por float. */
export function formatPesos(amount: string): string {
  const [whole = '0', cents = '00'] = amount.split('.');
  const grouped = whole.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  return cents === '00' || cents === '' ? `$${grouped}` : `$${grouped},${cents.padEnd(2, '0')}`;
}

/** Valida la tarifa escrita por el dueño: entero o con hasta 2 decimales (coma o punto). */
export function parsePrice(text: string): { ok: true; value: string | null } | { ok: false; error: string } {
  const clean = text.trim().replace(/\./g, '').replace(',', '.');
  if (clean === '') return { ok: true, value: null };
  if (!/^\d{1,8}(\.\d{1,2})?$/.test(clean)) {
    return { ok: false, error: 'Escribe la tarifa en pesos, por ejemplo 80000 o 80.000.' };
  }
  return { ok: true, value: clean };
}

export function slotCoversMatch(slot: Slot, kickoffAt: string, durationMinutes: number): boolean {
  const kickoff = Date.parse(kickoffAt);
  return (
    Date.parse(slot.starts_at) <= kickoff && kickoff + durationMinutes * 60_000 <= Date.parse(slot.ends_at)
  );
}

export type SlotFormResult = { ok: true; startsAt: string; endsAt: string } | { ok: false; error: string };

export function slotFromForm(startText: string, minutesText: string, now: Date): SlotFormResult {
  const start = parseLocalDateTime(startText);
  if (!start) return { ok: false, error: 'Escribe el inicio como dd/mm/aaaa hh:mm.' };
  if (Date.parse(start) <= now.getTime()) return { ok: false, error: 'La franja debe empezar en el futuro.' };
  const minutes = /^\d{2,3}$/.test(minutesText.trim()) ? Number(minutesText) : NaN;
  if (!(minutes >= 30 && minutes <= 240))
    return { ok: false, error: 'Una franja dura entre 30 y 240 minutos.' };
  return { ok: true, startsAt: start, endsAt: new Date(Date.parse(start) + minutes * 60_000).toISOString() };
}

export interface BookingActions {
  canBook: boolean;
  canCancelBooking: boolean;
}

export function bookingActions(contract: Contract, now: Date = new Date()): BookingActions {
  const signed = contract.signed;
  const open = contract.status !== 'CANCELLED' && contract.is_admin && signed !== null;
  const beforeKickoff = signed !== null && now.getTime() < Date.parse(signed.terms.kickoff_at);
  const active = contract.booking?.status === 'PENDING' || contract.booking?.status === 'CONFIRMED';
  return {
    canBook: open && beforeKickoff && signed?.terms.place_kind === 'VENUE' && !active,
    canCancelBooking: open && beforeKickoff && active,
  };
}
