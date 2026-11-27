// Qué puede hacer cada persona en una liga. El backend vuelve a validar todo.

import type { EntryKind, EntryStatus, LeagueDetail, MyLeague, StaffRole } from './leagueModels';
import type { MyTeam, User } from './models';

export const STAFF_ROLE_LABEL: Record<StaffRole, string> = {
  ORGANIZER: 'Organizador',
  CO_ORGANIZER: 'Coorganizador',
  REFEREE_COORDINATOR: 'Coordinador arbitral',
};

export const RELATION_LABEL: Record<MyLeague['relation'], string> = {
  ...STAFF_ROLE_LABEL,
  REFEREE: 'Árbitro de la liga',
  TEAM: 'Mi equipo juega aquí',
};

export const ENTRY_STATUS_LABEL: Record<EntryStatus, string> = {
  PENDING: 'Pendiente',
  APPROVED: 'Aprobado',
  REJECTED: 'Rechazado',
  WITHDRAWN: 'Retirado',
};

export function validateSeason(text: string): string | null {
  return /^\d{4}(-[12])?$/.test(text.trim()) ? null : 'Escribe la temporada como 2026, 2026-1 o 2026-2.';
}

export interface LeagueActions {
  /** Equipos que administro y aún pueden pedir inscripción (mismo deporte, modalidad y ciudad). */
  eligibleTeams: MyTeam[];
  canJoinAsReferee: boolean;
  canDecideTeams: boolean;
  canDecideReferees: boolean;
}

const sameKey = (a: string, b: string) =>
  a.trim().toLocaleLowerCase('es').normalize('NFD').replace(/\p{M}/gu, '') ===
  b.trim().toLocaleLowerCase('es').normalize('NFD').replace(/\p{M}/gu, '');

export function leagueActions(detail: LeagueDetail, user: User, myTeams: MyTeam[]): LeagueActions {
  const league = detail.league;
  const requested = new Set(detail.my_team_requests.map((e) => e.team.id));
  const eligibleTeams = myTeams.filter(
    (t) =>
      t.is_admin &&
      !requested.has(t.team.id) &&
      t.team.sport_code === league.sport_code &&
      t.team.modality_code === league.modality_code &&
      sameKey(t.team.city, league.city),
  );
  const role = detail.my_role;
  return {
    eligibleTeams,
    canJoinAsReferee:
      user.roles.includes('REFEREE') && user.sports.includes(league.sport_code) && !detail.my_referee_request,
    canDecideTeams: role === 'ORGANIZER' || role === 'CO_ORGANIZER',
    canDecideReferees: role !== null,
  };
}

export interface MyEntry {
  kind: EntryKind;
  id: number;
  name: string;
  status: EntryStatus;
}

/** Mis solicitudes activas en la liga: las de equipos que administro y la mía como árbitro. */
export function myEntries(detail: LeagueDetail): MyEntry[] {
  const teams = detail.my_team_requests.map((e) => ({
    kind: 'team' as const,
    id: e.id,
    name: e.team.name,
    status: e.status,
  }));
  const ref = detail.my_referee_request;
  return ref
    ? [...teams, { kind: 'referee', id: ref.id, name: 'Tú, como árbitro', status: ref.status }]
    : teams;
}
