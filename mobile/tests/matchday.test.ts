// Pruebas de las reglas locales del día del partido. Ejecutar: node --experimental-strip-types --test tests/
import assert from 'node:assert/strict';
import { test } from 'node:test';

import { levelText, parseScore } from '../src/domain/matchdayModels.ts';

test('texto del nivel con separador de miles y confiabilidad', () => {
  assert.equal(levelText(1612, true), 'Nivel 1.612 (confiable)');
  assert.equal(levelText(1540, false), 'Nivel 1.540 (aún incierto)');
  assert.equal(levelText(null, false), 'Sin nivel aún');
});

test('la valoración es un entero del 1 al 10', () => {
  assert.deepEqual(['1', '10', ' 7 '].map(parseScore), [1, 10, 7]);
  assert.deepEqual(['0', '11', '7.5', 'x', ''].map(parseScore), [null, null, null, null, null]);
});
