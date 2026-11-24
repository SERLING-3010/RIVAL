// Pruebas de las reglas locales de pendientes. Ejecutar: node --experimental-strip-types --test tests/
import assert from 'node:assert/strict';
import { test } from 'node:test';

import type { PendingItem } from '../src/domain/pendingModels.ts';
import { pendingCardTitle, urgency } from '../src/domain/pendingModels.ts';

const now = new Date('2026-11-24T15:00:00Z');
const item = (kind: string, due: string | null): PendingItem => ({
  kind,
  title: 't',
  detail: 'd',
  target: 'contract',
  target_id: 1,
  due_at: due,
});

test('urgente: partido en menos de 24 h o ya jugado, solo para tipos de partido', () => {
  assert.equal(urgency(item('SIGN_CONTRACT', '2026-11-25T10:00:00Z'), now), 'Urgente');
  assert.equal(urgency(item('REPORT_RESULT', '2026-11-20T10:00:00Z'), now), 'Urgente');
  assert.equal(urgency(item('SIGN_CONTRACT', '2026-11-28T10:00:00Z'), now), undefined);
  assert.equal(urgency(item('RATE_TEAMMATES', '2026-11-24T20:00:00Z'), now), undefined);
  assert.equal(urgency(item('CALLUP', null), now), undefined);
});

test('título de la tarjeta del inicio', () => {
  assert.equal(pendingCardTitle(null), 'Pendientes');
  assert.equal(pendingCardTitle(0), 'Sin pendientes');
  assert.equal(pendingCardTitle(3), 'Pendientes (3)');
});
