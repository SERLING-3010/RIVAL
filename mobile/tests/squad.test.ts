// Pruebas de la plantilla en modo juego. Ejecutar: node --experimental-strip-types --test tests/
import assert from 'node:assert/strict';
import { test } from 'node:test';

import type { PlayerCard } from '../src/domain/managerModels.ts';
import type { SquadCard } from '../src/domain/squadModels.ts';
import { compareAxes, pitchRows, roleMark, sortMembers } from '../src/domain/squadModels.ts';

const st = (id: number) => ({ user_id: id, position: null });

test('pitchRows: arquero abajo y líneas de la formación de atrás hacia adelante', () => {
  const rows = pitchRows('2-1-1', [st(1), st(2), st(3), st(4), st(5)]);
  assert.deepEqual(
    rows.map((r) => r.map((s) => s.user_id)),
    [[5], [4], [2, 3], [1]],
  );
  assert.deepEqual(
    pitchRows('3-3', [st(1), st(2), st(3)]).map((r) => r.length),
    [2, 1],
  ); // no cuadra: una fila de campo y el arquero
  assert.deepEqual(pitchRows(null, []), []);
});

const card = (id: number, media: number, matches: number, position: string | null): SquadCard => ({
  user_id: id,
  display_name: `J${id}`,
  position,
  role: 'PLAYER',
  media,
  tier: 'BRONCE',
  matches,
  goals: 0,
  wins: 0,
  rating_average: null,
  hat_tricks: 0,
  badges: 0,
});

test('sortMembers por media, partidos y posición', () => {
  const m = [card(1, 60, 9, 'Delantero'), card(2, 70, 3, 'Arquero'), card(3, 65, 12, 'Defensa')];
  assert.deepEqual(
    sortMembers(m, 'media').map((c) => c.user_id),
    [2, 3, 1],
  );
  assert.deepEqual(
    sortMembers(m, 'matches').map((c) => c.user_id),
    [3, 1, 2],
  );
  assert.deepEqual(
    sortMembers(m, 'position').map((c) => c.user_id),
    [2, 3, 1],
  );
  assert.equal(roleMark('CAPTAIN'), 'C');
  assert.equal(roleMark('PLAYER'), null);
});

const player = (matches: number, goals: number, rating: number | null, checkIns: number): PlayerCard => ({
  user_id: 1,
  display_name: 'X',
  position: null,
  sports: [],
  teams: [],
  matches,
  goals,
  wins: 0,
  draws: 0,
  losses: 0,
  rating_average: rating,
  rating_votes: 0,
  card: {
    media: 57,
    tier: 'BRONCE',
    next_tier: 'PLATA',
    display_tier: 'BRONCE',
    specials: [],
    media_to_next: 0,
    market_value: 480,
    hat_tricks: 0,
    check_ins: checkIns,
    recent: [],
    badges: [],
  },
});

test('compareAxes: seis ejes reales, valoración sobre 10 y nunca dividir por cero', () => {
  const axes = compareAxes(player(10, 4, 7.5, 3), player(5, 0, null, 0));
  assert.deepEqual(
    axes.map((a) => a.label),
    ['Partidos', 'Goles', 'Victorias', 'Valoración', 'Puntualidad', 'Insignias'],
  );
  assert.deepEqual([axes[0]?.max, axes[3]?.max, axes[5]?.max], [10, 10, 1]);
  assert.equal(axes[3]?.aText, '7,5');
});
