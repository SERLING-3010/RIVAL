// Pruebas de las reglas locales de moderación. Ejecutar: node --experimental-strip-types --test tests/
import assert from 'node:assert/strict';
import { test } from 'node:test';

import type { ModerationMe, Sanction } from '../src/domain/moderationModels.ts';
import { activeSuspension, canAppeal, textError } from '../src/domain/moderationModels.ts';

const now = new Date('2026-11-24T15:00:00Z');
const sanction = (overrides: Partial<Sanction>): Sanction => ({
  id: 1,
  kind: 'SUSPENSION',
  reason: 'Agresión',
  ends_at: '2026-11-27T15:00:00Z',
  status: 'ACTIVE',
  created_at: '2026-11-24T10:00:00Z',
  appeal_text: null,
  appeal_outcome: null,
  ...overrides,
});
const me = (sanctions: Sanction[]): ModerationMe => ({ is_moderator: false, sanctions });

test('suspensión vigente: activa y sin vencer; advertencias y revocadas no cuentan', () => {
  assert.equal(activeSuspension(me([sanction({})]), now)?.id, 1);
  assert.equal(activeSuspension(me([sanction({ ends_at: '2026-11-20T00:00:00Z' })]), now), null);
  assert.equal(activeSuspension(me([sanction({ status: 'REVOKED' })]), now), null);
  assert.equal(activeSuspension(me([sanction({ kind: 'WARNING', ends_at: null })]), now), null);
});

test('se apela una vez, con la sanción activa y dentro de 14 días', () => {
  assert.equal(canAppeal(sanction({}), now), true);
  assert.equal(canAppeal(sanction({ appeal_text: 'ya apelé' }), now), false);
  assert.equal(canAppeal(sanction({ status: 'REVOKED' }), now), false);
  assert.equal(canAppeal(sanction({ created_at: '2026-11-01T00:00:00Z' }), now), false);
});

test('longitud de textos', () => {
  assert.equal(
    textError('corto', 10, 500, 'La descripción'),
    'La descripción debe tener entre 10 y 500 caracteres.',
  );
  assert.equal(textError('  suficiente   texto ', 10, 500, 'X'), null);
});
