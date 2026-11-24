// Ejecutar: node --experimental-strip-types --test tests/dateTime.test.ts
import assert from 'node:assert/strict';
import { test } from 'node:test';

import { formatLocal, localTextInDays, parseLocalDateTime } from '../src/domain/dateTime.ts';
import { DISTANCE_LABEL } from '../src/domain/matchLabels.ts';

test('fecha y hora locales se envían con zona de Colombia', () => {
  assert.equal(parseLocalDateTime('28/11/2026 18:30'), '2026-11-28T18:30:00-05:00');
  assert.equal(parseLocalDateTime('5/11/2026 18:30'), null);
  assert.equal(parseLocalDateTime('31/11/2026 10:00'), null);
  assert.equal(parseLocalDateTime('28/11/2026 24:00'), null);
});

test('formatea en hora de Colombia aunque llegue en UTC', () => {
  assert.equal(formatLocal('2026-11-28T23:30:00Z'), 'sáb 28/11 18:30');
  assert.equal(formatLocal('2026-11-29T02:00:00+00:00'), 'sáb 28/11 21:00');
});

test('cambio de año al sumar días', () => {
  assert.equal(localTextInDays(new Date('2026-12-31T15:00:00Z'), 1, 9), '01/01/2027 09:00');
});

test('los rangos de distancia nunca muestran un punto exacto', () => {
  assert.deepEqual(Object.values(DISTANCE_LABEL), ['a menos de 2 km', 'a 2–5 km', 'a más de 5 km']);
});
