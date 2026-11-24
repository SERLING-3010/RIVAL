// Pruebas de las reglas locales. Ejecutar: node --experimental-strip-types --test tests/
import assert from 'node:assert/strict';
import { test } from 'node:test';

import { isAdult, parseBirthDate, validateRegistration } from '../src/domain/validation.ts';

const today = new Date(2026, 10, 23);

test('cumple 18 el día de su cumpleaños', () => {
  assert.equal(isAdult('2008-11-23', today), true);
  assert.equal(isAdult('2008-11-24', today), false);
});

test('29 de febrero cumple el 1 de marzo en año no bisiesto', () => {
  assert.equal(isAdult('2008-02-29', new Date(2026, 1, 28)), false);
  assert.equal(isAdult('2008-02-29', new Date(2026, 2, 1)), true);
});

test('fecha inexistente se rechaza', () => {
  assert.equal(parseBirthDate('31/02/2000'), null);
  assert.equal(parseBirthDate('05/10/1998'), '1998-10-05');
});

test('formulario de menor muestra el mensaje de edad', () => {
  const errors = validateRegistration(
    {
      role: 'PLAYER',
      displayName: 'José Peña',
      email: 'jose@rival.test',
      password: 'mi equipo juega los sábados',
      birthDate: '01/01/2012',
      sports: ['FOOTBALL'],
      city: 'Barranquilla',
      neighborhood: 'El Prado',
      position: '',
    },
    today,
  );
  assert.equal(errors.birthDate, 'Por ahora RIVAL es solo para mayores de 18 años.');
  assert.equal(errors.displayName, undefined);
});
