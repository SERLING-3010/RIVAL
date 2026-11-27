// Pruebas de las reglas locales de canchas y reservas. Ejecutar: node --experimental-strip-types --test tests/
import assert from 'node:assert/strict';
import { test } from 'node:test';

import type { Contract, ContractVersion } from '../src/domain/contractModels.ts';
import type { Booking, Slot } from '../src/domain/venueModels.ts';
import {
  bookingActions,
  formatPesos,
  parsePrice,
  slotCoversMatch,
  slotFromForm,
} from '../src/domain/venueRules.ts';

const now = new Date('2026-11-24T15:00:00Z');

test('pesos con separador de miles y sin pasar por float', () => {
  assert.equal(formatPesos('80000.00'), '$80.000');
  assert.equal(formatPesos('1250000.5'), '$1.250.000,50');
  assert.deepEqual(parsePrice('80.000'), { ok: true, value: '80000' });
  assert.deepEqual(parsePrice('80000,50'), { ok: true, value: '80000.50' });
  assert.deepEqual(parsePrice(''), { ok: true, value: null });
  assert.equal(parsePrice('10,555').ok, false);
});

test('la franja cubre el partido completo', () => {
  const slot: Slot = {
    id: 1,
    court_id: 1,
    court_name: 'C1',
    sport_code: 'FOOTBALL',
    starts_at: '2026-11-25T23:00:00Z',
    ends_at: '2026-11-26T01:00:00Z',
  };
  assert.equal(slotCoversMatch(slot, '2026-11-25T23:30:00Z', 90), true);
  assert.equal(slotCoversMatch(slot, '2026-11-25T23:31:00Z', 90), false);
  assert.equal(slotCoversMatch(slot, '2026-11-25T22:59:00Z', 60), false);
});

test('formulario de franja: hora de Colombia, futuro y duración 30–240', () => {
  const ok = slotFromForm('26/11/2026 18:00', '90', now);
  assert.deepEqual(ok, {
    ok: true,
    startsAt: '2026-11-26T18:00:00-05:00',
    endsAt: '2026-11-27T00:30:00.000Z', // 18:00 en Colombia = 23:00 UTC, más 90 min
  });
  assert.equal(slotFromForm('01/11/2026 18:00', '90', now).ok, false);
  assert.equal(slotFromForm('26/11/2026 18:00', '20', now).ok, false);
  assert.equal(slotFromForm('26/11/2026 18:00', '300', now).ok, false);
});

const version = (place: 'VENUE' | 'INFORMAL'): ContractVersion => ({
  version: 1,
  proposed_by_side: null,
  note: null,
  created_at: '',
  signed_by: ['HOST', 'GUEST'],
  terms: {
    kickoff_at: '2026-11-26T01:00:00Z',
    duration_minutes: 60,
    referee_mode: 'WITHOUT',
    place_kind: place,
    place_note: null,
    host_kit_color: 'Rojo',
    guest_kit_color: 'Azul',
    substitutions: null,
    field_cost_split: 'HALF',
    referee_cost_split: 'HALF',
    cancellation_notice_hours: 24,
    foul_caller_note: null,
    extra_rules: null,
  },
});

function contract(overrides: Partial<Contract>): Contract {
  const team = {
    id: 1,
    name: 'A',
    sport_code: 'FOOTBALL',
    modality_code: 'F7',
    city: 'B',
    neighborhood: 'N',
    member_count: 5,
    has_coach: true,
  };
  return {
    id: 1,
    request_id: 1,
    host: team,
    guest: { ...team, id: 2 },
    status: 'SIGNED',
    my_side: 'HOST',
    is_admin: true,
    is_staff: true,
    current: version('VENUE'),
    signed: version('VENUE'),
    versions: [],
    cancel_reason: null,
    result: null,
    booking: null,
    ready_to_play: false,
    referee: null,
    league_id: null,
    ...overrides,
  };
}

test('reservar: solo firmado, en establecimiento, antes de la hora y sin reserva activa', () => {
  assert.deepEqual(bookingActions(contract({}), now), { canBook: true, canCancelBooking: false });
  assert.equal(bookingActions(contract({ signed: version('INFORMAL') }), now).canBook, false);
  assert.equal(bookingActions(contract({ signed: null, status: 'NEGOTIATING' }), now).canBook, false);
  assert.equal(bookingActions(contract({ is_admin: false }), now).canBook, false);
  assert.equal(bookingActions(contract({}), new Date('2026-11-26T02:00:00Z')).canBook, false);
  const pending = { status: 'PENDING' } as Booking;
  assert.deepEqual(bookingActions(contract({ booking: pending }), now), {
    canBook: false,
    canCancelBooking: true,
  });
  const rejected = { status: 'REJECTED' } as Booking;
  assert.equal(bookingActions(contract({ booking: rejected }), now).canBook, true);
});
