// Pruebas de las reglas locales del modo manager. Ejecutar: node --experimental-strip-types --test tests/
import assert from 'node:assert/strict';
import { test } from 'node:test';

import type { SquadMember } from '../src/domain/managerModels.ts';
import { canBeListed, formatCoins, lineupFromForm, parseOffer } from '../src/domain/managerRules.ts';

test('monedas con separador de miles', () => {
  assert.equal(formatCoins(1250), '1.250 RC');
  assert.equal(formatCoins(-300), '−300 RC');
});

test('la oferta respeta el rango y el presupuesto', () => {
  assert.deepEqual(parseOffer('1.000', 5000), { ok: true, amount: 1000 });
  assert.equal(parseOffer('0', 5000).ok, false);
  assert.equal(parseOffer('abc', 5000).ok, false);
  assert.deepEqual(parseOffer('600', 500), { ok: false, error: 'Tu equipo tiene 500 RC.' });
});

test('solo jugadores rasos se ponen en el mercado', () => {
  const member = (role: SquadMember['role']): SquadMember => ({
    user_id: 1,
    display_name: 'Ana',
    role,
    position: null,
    listed: false,
    matches: 0,
    goals: 0,
  });
  assert.deepEqual(
    ['PLAYER', 'CAPTAIN', 'COACH'].map((r) => canBeListed(member(r as SquadMember['role']))),
    [true, false, false],
  );
});

test('planilla: al menos un jugador, goles válidos y sin superar el marcador', () => {
  assert.deepEqual(lineupFromForm([1, 2], { 1: '2' }, 2), {
    ok: true,
    players: [
      { user_id: 1, goals: 2 },
      { user_id: 2, goals: 0 },
    ],
  });
  assert.equal(lineupFromForm([], {}, 0).ok, false);
  assert.equal(lineupFromForm([1], { 1: 'x' }, 3).ok, false);
  assert.deepEqual(lineupFromForm([1, 2], { 1: '2', 2: '1' }, 2), {
    ok: false,
    error: 'La suma de goles supera el marcador de tu equipo (2).',
  });
});
