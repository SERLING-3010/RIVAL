// Pruebas de las reglas locales del contrato. Ejecutar: node --experimental-strip-types --test tests/
import assert from 'node:assert/strict';
import { test } from 'node:test';

import { formFromTerms, termsFromForm } from '../src/domain/contractForm.ts';
import type { Contract, ContractTerms } from '../src/domain/contractModels.ts';
import { changedFields, contractActions } from '../src/domain/contractRules.ts';

const now = new Date('2026-11-23T15:00:00Z');

const terms: ContractTerms = {
  kickoff_at: '2026-11-25T01:00:00+00:00',
  duration_minutes: 60,
  referee_mode: 'WITHOUT',
  place_kind: 'INFORMAL',
  place_note: 'Parque',
  host_kit_color: 'Oscuro',
  guest_kit_color: 'Claro',
  substitutions: null,
  field_cost_split: 'HALF',
  referee_cost_split: 'HALF',
  cancellation_notice_hours: 24,
  foul_caller_note: null,
  extra_rules: null,
};

const team = {
  id: 1,
  name: 'Águilas',
  sport_code: 'FOOTBALL',
  modality_code: 'F7',
  city: 'B',
  neighborhood: 'N',
  member_count: 5,
  has_coach: true,
};

function contract(overrides: Partial<Contract>): Contract {
  const version = { version: 1, terms, proposed_by_side: null, note: null, created_at: '', signed_by: [] };
  return {
    id: 1,
    request_id: 1,
    host: team,
    guest: { ...team, id: 2 },
    status: 'NEGOTIATING',
    my_side: 'HOST',
    is_admin: true,
    current: version,
    signed: null,
    versions: [version],
    cancel_reason: null,
    ...overrides,
  };
}

test('el formulario conserva las condiciones sin cambios (ida y vuelta)', () => {
  const result = termsFromForm(formFromTerms(terms), now);
  assert.equal(result.ok, true);
  if (result.ok) assert.deepEqual(changedFields(terms, result.terms), ['kickoff_at']);
  if (result.ok) assert.equal(Date.parse(result.terms.kickoff_at), Date.parse(terms.kickoff_at));
});

test('uniformes iguales sin importar mayúsculas se rechazan', () => {
  const result = termsFromForm({ ...formFromTerms(terms), guestKit: ' OSCURO ' }, now);
  assert.deepEqual(result, { ok: false, error: 'Los uniformes deben ser de colores distintos.' });
});

test('duración y cambios fuera de rango se rechazan; cambios vacíos = ilimitados', () => {
  assert.equal(termsFromForm({ ...formFromTerms(terms), duration: '10' }, now).ok, false);
  assert.equal(termsFromForm({ ...formFromTerms(terms), substitutions: '31' }, now).ok, false);
  const unlimited = termsFromForm({ ...formFromTerms(terms), substitutions: '' }, now);
  assert.equal(unlimited.ok && unlimited.terms.substitutions, null);
});

test('una hora pasada se rechaza', () => {
  assert.equal(termsFromForm({ ...formFromTerms(terms), kickoff: '01/11/2026 10:00' }, now).ok, false);
});

test('quién puede firmar: solo el administrador que aún no firmó', () => {
  assert.equal(contractActions(contract({})).canSign, true);
  const signedByMe = contract({ current: { ...contract({}).current, signed_by: ['HOST'] } });
  assert.equal(contractActions(signedByMe).canSign, false);
  assert.match(contractActions(signedByMe).status, /rival/);
  assert.equal(contractActions(contract({ is_admin: false })).canSign, false);
  const cancelled = contractActions(contract({ status: 'CANCELLED' }));
  assert.equal(cancelled.canCancel || cancelled.canPropose, false);
});

test('un cambio sobre un contrato firmado se puede rechazar y avisa que vale la versión firmada', () => {
  const base = contract({});
  const amended = contract({
    signed: base.current,
    current: { ...base.current, version: 2, signed_by: ['GUEST'] },
  });
  const actions = contractActions(amended);
  assert.equal(actions.canRejectAmendment, true);
  assert.match(actions.status, /versión firmada/);
});
