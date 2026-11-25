// Pruebas de las cartas nuevas. Ejecutar: node --experimental-strip-types --test tests/
import assert from 'node:assert/strict';
import { test } from 'node:test';

import type { SpecialCard } from '../src/domain/cardModels.ts';
import { SPECIAL_CODES } from '../src/domain/cardTiers.ts';
import { earnedSignature, markSeen, seenKey, toReveal, unseenSpecials } from '../src/domain/newCards.ts';

const specials = (earned: string[]): SpecialCard[] =>
  SPECIAL_CODES.map((code) => ({
    code,
    min_media: 75,
    earned_at: earned.includes(code) ? '2026-11-25T12:00:00Z' : null,
    goals: [],
  }));

test('se revela la especial ganada más difícil que aún no se vio', () => {
  const s = specials(['RUBI', 'ESMERALDA', 'DIAMANTE']);
  assert.deepEqual(unseenSpecials(s, ['RUBI']), ['ESMERALDA', 'DIAMANTE']);
  assert.equal(toReveal(s, ['RUBI']), 'DIAMANTE');
  assert.equal(toReveal(s, ['RUBI', 'ESMERALDA', 'DIAMANTE']), null);
  assert.equal(toReveal(specials([]), []), null);
});

test('al cerrar, todas las nuevas quedan vistas; la clave separa persona y dueño', () => {
  const s = specials(['RUBI', 'ESMERALDA']);
  assert.deepEqual(markSeen(s, ['RUBI']), ['RUBI', 'ESMERALDA']);
  assert.equal(seenKey('team', 4, 9), 'rival.seen.team.9.4');
  assert.equal(earnedSignature(s), 'RUBI,ESMERALDA');
  assert.equal(earnedSignature(null), '');
});
