// Pruebas de la carta del jugador. Ejecutar: node --experimental-strip-types --test tests/
import assert from 'node:assert/strict';
import { test } from 'node:test';

import { frontStats, goalsPerMatch, initials, nextTierText } from '../src/domain/cardModels.ts';
import type { PlayerCard } from '../src/domain/managerModels.ts';

const player = (over: Partial<PlayerCard> = {}): PlayerCard => ({
  user_id: 1,
  display_name: 'Andrés Mejía',
  position: 'Delantero',
  sports: ['FOOTBALL'],
  teams: [],
  matches: 24,
  goals: 18,
  wins: 14,
  draws: 4,
  losses: 6,
  rating_average: 8.1,
  rating_votes: 19,
  card: {
    media: 78,
    tier: 'ORO',
    next_tier: 'ELITE',
    matches_to_next: 6,
    hat_tricks: 2,
    recent: ['W', 'W', 'D', 'L', 'W'],
    badges: ['Debut', 'Goleador'],
  },
  ...over,
});

test('initials: dos letras o una, nunca vacío', () => {
  assert.equal(initials('Chuchuwaza'), 'C');
  assert.equal(initials('Rivales de Prueba'), 'RP');
  assert.equal(initials('   '), '?');
});

test('frontStats: las seis estadísticas reales en orden', () => {
  assert.deepEqual(
    frontStats(player()).map((s) => `${s.value} ${s.label}`),
    ['24 PJ', '14 VIC', '18 GOL', '8,1 VAL', '2 TRI', '2 INS'],
  );
  assert.equal(frontStats(player({ rating_average: null }))[3]?.value, '–');
});

test('nextTierText y goalsPerMatch', () => {
  assert.equal(nextTierText(player().card), 'Faltan 6 partidos para Élite');
  assert.equal(nextTierText({ ...player().card, matches_to_next: 1 }), 'Falta 1 partido para Élite');
  assert.equal(
    nextTierText({ ...player().card, tier: 'ELITE', next_tier: null, matches_to_next: 0 }),
    'Nivel máximo: Élite',
  );
  assert.equal(goalsPerMatch(player()), '0,75');
  assert.equal(goalsPerMatch(player({ matches: 0, goals: 0 })), '0');
});
