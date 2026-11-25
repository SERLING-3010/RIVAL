// Pruebas de la copa eliminatoria. Ejecutar: node --experimental-strip-types --test tests/
import assert from 'node:assert/strict';
import { test } from 'node:test';

import type { CupMatch } from '../src/domain/cupModels.ts';
import { matchLine, parseSchedule } from '../src/domain/cupModels.ts';

const m = (over: Partial<CupMatch> = {}): CupMatch => ({
  id: 1,
  position: 0,
  host_team_id: 1,
  guest_team_id: 2,
  host_name: 'Águilas',
  guest_name: 'Bravos',
  contract_id: 9,
  host_score: null,
  guest_score: null,
  winner_name: null,
  needs_tiebreak: false,
  ...over,
});

test('matchLine: cruce, marcador, pase directo y por definir', () => {
  assert.equal(matchLine(m(), false), 'Águilas vs Bravos');
  assert.equal(matchLine(m({ host_score: 2, guest_score: 1 }), false), 'Águilas 2 – 1 Bravos');
  assert.equal(matchLine(m({ guest_name: null, guest_team_id: null }), true), 'Águilas (pasa directo)');
  assert.equal(matchLine(m({ guest_name: null, guest_team_id: null }), false), 'Águilas vs Por definir');
  assert.equal(matchLine(m({ host_name: null, guest_name: null }), false), 'Por definir vs Por definir');
});

test('parseSchedule: fecha válida y de 1 a 14 días', () => {
  assert.deepEqual(parseSchedule('05/12/2026 18:00', '7'), {
    ok: true,
    first: '2026-12-05T18:00:00-05:00',
    days: 7,
  });
  assert.equal(parseSchedule('mañana', '7').ok, false);
  assert.equal(parseSchedule('05/12/2026 18:00', '15').ok, false);
});
