// Pruebas del chat del partido. Ejecutar: node --experimental-strip-types --test tests/
import assert from 'node:assert/strict';
import { test } from 'node:test';

import type { ChatMessage } from '../src/domain/chatModels.ts';
import { draftError, lastId, mergeMessages, messageText } from '../src/domain/chatModels.ts';

const msg = (id: number, body: string | null = `m${id}`): ChatMessage => ({
  id,
  author_id: 1,
  author_name: 'Ana',
  body,
  created_at: '2026-11-24T20:00:00Z',
  deleted: body === null,
  mine: false,
});

test('mergeMessages: une sin repetir, en orden y con la versión más reciente', () => {
  const merged = mergeMessages([msg(1), msg(3)], [msg(3, null), msg(2), msg(4)]);
  assert.deepEqual(
    merged.map((m) => m.id),
    [1, 2, 3, 4],
  );
  assert.equal(merged[2]?.deleted, true);
  assert.equal(lastId(merged), 4);
  assert.equal(lastId([]), 0);
});

test('messageText muestra "Mensaje eliminado" si el autor lo borró', () => {
  assert.equal(messageText(msg(1, null)), 'Mensaje eliminado');
  assert.equal(messageText(msg(1, 'Hola')), 'Hola');
});

test('draftError: vacío o muy largo no se envía', () => {
  assert.equal(draftError('   '), 'Escribe un mensaje.');
  assert.equal(draftError('x'.repeat(501)), 'Máximo 500 caracteres.');
  assert.equal(draftError('  Nos vemos  '), null);
});
