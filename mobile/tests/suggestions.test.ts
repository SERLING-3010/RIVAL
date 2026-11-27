// Pruebas de rivales sugeridos. Ejecutar: node --experimental-strip-types --test tests/
import assert from 'node:assert/strict';
import { test } from 'node:test';

import type { Suggestion } from '../src/domain/suggestionModels.ts';
import { suggestionSubtitle } from '../src/domain/suggestionModels.ts';

const s = (level: number | null): Suggestion => ({
  team: {
    id: 2,
    name: 'Bravos',
    sport_code: 'FOOTBALL',
    modality_code: 'F7',
    city: 'Barranquilla',
    neighborhood: 'El Prado',
    member_count: 7,
    has_coach: true,
  } as Suggestion['team'],
  distance_band: 'UNDER_2_KM',
  level,
  reasons: ['Está a menos de 2 km'],
});

test('suggestionSubtitle: barrio y nivel, o "sin nivel aún"', () => {
  assert.equal(suggestionSubtitle(s(1520)), 'El Prado · Nivel 1520');
  assert.equal(suggestionSubtitle(s(null)), 'El Prado · Sin nivel aún');
});
