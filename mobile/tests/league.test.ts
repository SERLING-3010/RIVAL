// Pruebas de las reglas locales de ligas. Ejecutar: node --experimental-strip-types --test tests/
import assert from 'node:assert/strict';
import { test } from 'node:test';

import type { LeagueDetail } from '../src/domain/leagueModels.ts';
import { leagueActions, myEntries, validateSeason } from '../src/domain/leagueRules.ts';
import type { MyTeam, TeamSummary, User } from '../src/domain/models.ts';

const team = (id: number, overrides: Partial<TeamSummary> = {}): TeamSummary => ({
  id,
  name: `Equipo ${id}`,
  sport_code: 'FOOTBALL',
  modality_code: 'F7',
  city: 'Barranquilla',
  neighborhood: 'El Prado',
  member_count: 7,
  has_coach: true,
  ...overrides,
});

const mine = (summary: TeamSummary, isAdmin = true): MyTeam => ({
  team: summary,
  my_role: 'COACH',
  is_admin: isAdmin,
  pending_requests: 0,
});

const user: User = {
  id: 9,
  email: 'x@r.test',
  display_name: 'Ana',
  roles: ['COACH'],
  sports: ['FOOTBALL'],
  city: 'Barranquilla',
  neighborhood: 'El Prado',
  position: null,
};

function detail(overrides: Partial<LeagueDetail> = {}): LeagueDetail {
  return {
    league: {
      id: 1,
      name: 'Liga',
      sport_code: 'FOOTBALL',
      modality_code: 'F7',
      city: 'barranquilla',
      season: '2026-2',
      team_count: 0,
      referee_count: 0,
    },
    description: null,
    my_role: null,
    transfer_window_start: null,
    transfer_window_end: null,
    staff: [],
    teams: [],
    referees: [],
    pending_teams: [],
    pending_referees: [],
    my_team_requests: [],
    my_referee_request: null,
    ...overrides,
  };
}

test('temporada válida', () => {
  assert.equal(validateSeason('2026-2'), null);
  assert.notEqual(validateSeason('2026-3'), null);
});

test('solo equipos que administro, del mismo juego y ciudad (sin tildes ni mayúsculas), y sin solicitud', () => {
  const teams = [
    mine(team(1)),
    mine(team(2, { modality_code: 'F11' })),
    mine(team(3), false),
    mine(team(4, { city: 'BARRANQUÍLLA' })),
    mine(team(5)),
  ];
  const requested = detail({ my_team_requests: [{ id: 50, team: team(5), status: 'PENDING' }] });
  assert.deepEqual(
    leagueActions(requested, user, teams).eligibleTeams.map((t) => t.team.id),
    [1, 4],
  );
});

test('árbitro con el deporte puede unirse; el coordinador decide árbitros pero no equipos', () => {
  const referee = { ...user, roles: ['REFEREE' as const] };
  assert.equal(leagueActions(detail(), referee, []).canJoinAsReferee, true);
  assert.equal(leagueActions(detail(), { ...referee, sports: ['BASKETBALL'] }, []).canJoinAsReferee, false);
  const coordinator = leagueActions(detail({ my_role: 'REFEREE_COORDINATOR' }), user, []);
  assert.deepEqual([coordinator.canDecideTeams, coordinator.canDecideReferees], [false, true]);
});

test('mis solicitudes incluyen la de árbitro', () => {
  const entries = myEntries(
    detail({
      my_team_requests: [{ id: 3, team: team(1), status: 'APPROVED' }],
      my_referee_request: { id: 8, user_id: 9, display_name: 'Ana', status: 'PENDING' },
    }),
  );
  assert.deepEqual(
    entries.map((e) => `${e.kind}:${e.id}:${e.status}`),
    ['team:3:APPROVED', 'referee:8:PENDING'],
  );
});
