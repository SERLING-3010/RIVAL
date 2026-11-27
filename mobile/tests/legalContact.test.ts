// Datos del responsable desde el servidor (Sprint 29). Ejecutar: node --experimental-strip-types --test tests/
import assert from 'node:assert/strict';
import { test } from 'node:test';

import { EMPTY_CONTACT, fillLegal, privacyMailto } from '../src/domain/legalContact.ts';
import { PRIVACY } from '../src/domain/legalPrivacy.ts';

test('la política se llena con lo que manda el servidor; lo vacío queda «por definir»', () => {
  const filled = fillLegal(PRIVACY, { ...EMPTY_CONTACT, name: 'RIVAL S.A.S.', email: 'privacidad@rival.co' });
  const responsable = filled.find((s) => s.title === 'Responsable del tratamiento')?.body ?? '';
  assert.match(responsable, /RIVAL S\.A\.S\./);
  assert.match(responsable, /Teléfono: por definir/);
  assert.doesNotMatch(responsable, /Cédula|NIT/); // la ley no lo pide (Decreto 1377, art. 13)
  assert.ok(filled.every((s) => !/\{\w+\}/.test(s.body))); // no queda ningún marcador sin llenar
});

test('el correo de privacidad solo se ofrece si hay uno válido', () => {
  assert.equal(privacyMailto(EMPTY_CONTACT), null);
  const mail = privacyMailto({ ...EMPTY_CONTACT, email: 'privacidad@rival.co' }) ?? '';
  assert.ok(mail.startsWith('mailto:privacidad@rival.co?subject='));
});
