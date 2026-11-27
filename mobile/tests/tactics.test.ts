// Pruebas de la alineación táctica. Ejecutar: node --experimental-strip-types --test tests/
import assert from 'node:assert/strict';
import { test } from 'node:test';

import type { Tactic, TacticSlot } from '../src/domain/tacticsModels.ts';
import { draftBody, draftFrom, draftProblem } from '../src/domain/tacticsModels.ts';

const slot = (id: number, position: string | null = null): TacticSlot => ({
  user_id: id,
  display_name: `J${id}`,
  position,
  still_going: true,
});

const tactic = (over: Partial<Tactic> = {}): Tactic => ({
  contract_id: 7,
  team_id: 1,
  players_per_side: 3,
  uses_formation: true,
  suggested_formations: ['1-1'],
  formation: null,
  starters: [],
  subs: [],
  eligible: [slot(1), slot(2), slot(3), slot(4)],
  can_edit: true,
  ...over,
});

test('draftFrom pone a todos fuera y respeta lo guardado', () => {
  const saved = draftFrom(tactic({ starters: [slot(1, 'Arquero')], subs: [slot(2)], eligible: [slot(3)] }));
  assert.deepEqual(saved.roles, { 1: 'starter', 2: 'sub', 3: 'out' });
  assert.equal(saved.positions[1], 'Arquero');
});

test('draftProblem: titulares exactos, posiciones y formación que suma sin el arquero', () => {
  const t = tactic();
  const d = draftFrom(t);
  assert.equal(draftProblem(d, t), 'Elige exactamente 3 titulares.');
  d.roles = { 1: 'starter', 2: 'starter', 3: 'starter', 4: 'sub' };
  assert.equal(draftProblem(d, t), 'Escribe la posición de cada titular.');
  d.positions = { 1: 'Arquero', 2: 'Defensa', 3: 'Delantero' };
  d.formation = '2-1';
  assert.match(draftProblem(d, t) ?? '', /sumar 2/);
  d.formation = '1-1';
  assert.equal(draftProblem(d, t), null);
  assert.deepEqual(draftBody(d, t), {
    formation: '1-1',
    starters: [
      { user_id: 1, position: 'Arquero' },
      { user_id: 2, position: 'Defensa' },
      { user_id: 3, position: 'Delantero' },
    ],
    subs: [4],
  });
});

test('sin formación en deportes que no la usan', () => {
  const t = tactic({ uses_formation: false });
  const d = { formation: '2-1', roles: {}, positions: {} };
  assert.equal(draftBody(d, t).formation, null);
});
