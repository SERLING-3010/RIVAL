// Pruebas de las reglas locales de la temporada. Ejecutar: node --experimental-strip-types --test tests/
import assert from 'node:assert/strict';
import { test } from 'node:test';

import type { Fixture, RefereeMatch } from '../src/domain/seasonModels.ts';
import { canRefereeReport, groupByRound } from '../src/domain/seasonModels.ts';

const team = (id: number) => ({
  id,
  name: `E${id}`,
  sport_code: 'FOOTBALL',
  modality_code: 'F7',
  city: 'B',
  neighborhood: 'N',
  member_count: 7,
  has_coach: true,
});

const fixture = (round: number, id: number): Fixture => ({
  round,
  contract_id: id,
  host: team(1),
  guest: team(2),
  kickoff_at: '2026-11-28T23:00:00Z',
  status: 'NEGOTIATING',
  result: null,
});

test('agrupa el calendario por fecha en orden', () => {
  const grouped = groupByRound([fixture(2, 3), fixture(1, 1), fixture(1, 2)]);
  assert.deepEqual(
    grouped.map((g) => [g.round, g.matches.map((m) => m.contract_id)]),
    [
      [1, [1, 2]],
      [2, [3]],
    ],
  );
});

test('el árbitro fija resultado solo si aceptó, ya pasó la hora y no está confirmado', () => {
  const match: RefereeMatch = {
    assignment_id: 1,
    contract_id: 9,
    status: 'ACCEPTED',
    league_name: 'Liga',
    host_name: 'A',
    guest_name: 'B',
    kickoff_at: '2026-11-28T23:00:00Z',
    place_kind: 'TO_AGREE',
    place_note: null,
    result_status: 'DISPUTED',
    host_score: null,
    guest_score: null,
  };
  const after = new Date('2026-11-29T01:00:00Z');
  assert.equal(canRefereeReport(match, after), true);
  assert.equal(canRefereeReport(match, new Date('2026-11-28T22:00:00Z')), false);
  assert.equal(canRefereeReport({ ...match, status: 'PENDING' }, after), false);
  assert.equal(canRefereeReport({ ...match, result_status: 'CONFIRMED' }, after), false);
});
