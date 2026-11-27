// Pruebas del alcance del lanzamiento (Sprint 29). Ejecutar: node --experimental-strip-types --test tests/
import assert from 'node:assert/strict';
import { test } from 'node:test';

import { ALL_FEATURES, placeChoices, refereeChoices, roleOptions } from '../src/domain/features.ts';
import { ROLE_OPTIONS } from '../src/domain/labels.ts';

const launch = { sports: ['FOOTBALL'], referees: false, venues: false };

test('en el lanzamiento solo hay jugadores y DT', () => {
  assert.deepEqual(
    roleOptions(ROLE_OPTIONS, launch).map((o) => o.role),
    ['PLAYER', 'COACH'],
  );
  assert.equal(roleOptions(ROLE_OPTIONS, ALL_FEATURES).length, 4);
});

test('sin árbitros solo queda «sin árbitro»; sin canchas no hay establecimiento', () => {
  assert.deepEqual(refereeChoices(['EITHER', 'WITH', 'WITHOUT'], launch), ['WITHOUT']);
  assert.deepEqual(placeChoices(['TO_AGREE', 'INFORMAL', 'VENUE'], launch), ['TO_AGREE', 'INFORMAL']);
  assert.deepEqual(refereeChoices(['WITHOUT', 'WITH'], ALL_FEATURES), ['WITHOUT', 'WITH']);
});
