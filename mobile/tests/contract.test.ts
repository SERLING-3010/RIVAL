// Pruebas de las reglas locales del contrato. Ejecutar: node --experimental-strip-types --test tests/
import assert from 'node:assert/strict';
import { test } from 'node:test';

import { formFromTerms, termsFromForm } from '../src/domain/contractForm.ts';
import type { Contract, ContractTerms } from '../src/domain/contractModels.ts';
import { actionLabel, actorText, changeLines } from '../src/domain/activityLabels.ts';
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
    result: null,
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
  assert.equal(contractActions(contract({}), now).canSign, true);
  const signedByMe = contract({ current: { ...contract({}).current, signed_by: ['HOST'] } });
  assert.equal(contractActions(signedByMe, now).canSign, false);
  assert.match(contractActions(signedByMe, now).status, /rival/);
  assert.equal(contractActions(contract({ is_admin: false }), now).canSign, false);
  const cancelled = contractActions(contract({ status: 'CANCELLED' }), now);
  assert.equal(cancelled.canCancel || cancelled.canPropose, false);
});

test('un cambio sobre un contrato firmado se puede rechazar y avisa que vale la versión firmada', () => {
  const base = contract({});
  const amended = contract({
    signed: base.current,
    current: { ...base.current, version: 2, signed_by: ['GUEST'] },
  });
  const actions = contractActions(amended, now);
  assert.equal(actions.canRejectAmendment, true);
  assert.match(actions.status, /versión firmada/);
});

test('después de la hora: no se cambia ni se cancela; se reporta si estaba firmado', () => {
  const later = new Date('2026-11-26T00:00:00Z');
  const signed = contract({ status: 'SIGNED', signed: contract({}).current });
  const actions = contractActions(signed, later);
  assert.deepEqual([actions.canPropose, actions.canCancel, actions.canReportResult], [false, false, true]);
  assert.equal(contractActions(signed, now).canReportResult, false);
  assert.equal(contractActions(contract({}), later).canReportResult, false);
  const done = { status: 'CONFIRMED' as const, host_score: 1, guest_score: 0, reports: [] };
  assert.equal(contractActions({ ...signed, result: done }, later).canReportResult, false);
});

test('la actividad muestra antes → después solo de campos conocidos', () => {
  const item = {
    occurred_at: '2026-11-23T15:00:00Z',
    action: 'CONTRACT_VERSION_PROPOSED',
    entity: 'match_contract',
    entity_id: '1',
    actor_type: 'HUMAN',
    actor_name: 'José',
    approver_name: null,
    before: { duration_minutes: 60 },
    after: { duration_minutes: 90, version: 2 },
  };
  assert.equal(actionLabel(item.action), 'Propuso cambios al contrato');
  assert.deepEqual(changeLines(item), ['duración: 60 → 90']);
  assert.equal(
    actorText({ ...item, actor_name: null, actor_type: 'SYSTEM_RULE' }),
    'RIVAL (regla automática)',
  );
});
