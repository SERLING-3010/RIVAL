// Pruebas del check-in en la cancha. Ejecutar: node --experimental-strip-types --test tests/
import assert from 'node:assert/strict';
import { test } from 'node:test';

import type { CheckInBoard } from '../src/domain/checkInModels.ts';
import { checkInStep } from '../src/domain/checkInModels.ts';

const board = (over: Partial<CheckInBoard> = {}): CheckInBoard => ({
  contract_id: 7,
  unavailable: null,
  venue_name: 'Canchas El Prado',
  opens_at: '2026-11-28T17:00:00-05:00',
  closes_at: '2026-11-28T19:00:00-05:00',
  window_open: false,
  me_checked_in: false,
  items: [],
  ...over,
});

test('checkInStep: sin cancha, ya hecho, abierto, aún no o cerrado', () => {
  const before = new Date('2026-11-28T20:00:00Z'); // 15:00 en Colombia
  const after = new Date('2026-11-29T02:00:00Z'); // 21:00 en Colombia
  assert.equal(checkInStep(board({ unavailable: 'Sin cancha' }), before), 'unavailable');
  assert.equal(checkInStep(board({ me_checked_in: true, window_open: true }), before), 'done');
  assert.equal(checkInStep(board({ window_open: true }), before), 'open');
  assert.equal(checkInStep(board(), before), 'notYet');
  assert.equal(checkInStep(board(), after), 'closed');
});
