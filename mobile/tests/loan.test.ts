// Pruebas de préstamos y ventana de traspasos. Ejecutar: node --experimental-strip-types --test tests/
import assert from 'node:assert/strict';
import { test } from 'node:test';

import { borrowable, parseWindow, windowText } from '../src/domain/loanModels.ts';

const fmt = (iso: string) => iso.slice(0, 10);
const start = '2026-12-01T00:00:00-05:00';
const end = '2026-12-15T00:00:00-05:00';

test('ventana: sin fechas está abierta; antes, durante y después', () => {
  assert.equal(windowText(null, null, new Date(), fmt), 'Sin ventana: los traspasos están abiertos.');
  assert.match(windowText(start, end, new Date('2026-11-24T12:00:00Z'), fmt), /cerrada\. Abre el 2026-12-01/);
  assert.match(windowText(start, end, new Date('2026-12-05T12:00:00Z'), fmt), /abierta hasta el 2026-12-15/);
  assert.match(windowText(start, end, new Date('2026-12-20T12:00:00Z'), fmt), /cerrada desde el 2026-12-15/);
});

test('parseWindow: formato, orden y valores ISO en hora de Colombia', () => {
  assert.deepEqual(parseWindow('01/12/2026 00:00', '15/12/2026 00:00'), { ok: true, start, end });
  assert.equal(parseWindow('2026-12-01', '15/12/2026 00:00').ok, false);
  const inverted = parseWindow('15/12/2026 00:00', '01/12/2026 00:00');
  assert.deepEqual(inverted, { ok: false, error: 'El cierre debe ser después de la apertura.' });
});

test('borrowable: solo jugadores sin préstamo abierto en el partido', () => {
  const members = [
    { user_id: 1, role: 'COACH' },
    { user_id: 2, role: 'CAPTAIN' },
    { user_id: 3, role: 'PLAYER' },
    { user_id: 4, role: 'PLAYER' },
  ];
  assert.deepEqual(
    borrowable(members, [4]).map((m) => m.user_id),
    [3],
  );
});
