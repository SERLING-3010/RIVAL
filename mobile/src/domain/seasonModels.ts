// Calendario y tabla de la liga, y partidos del árbitro (Sprint 8).

import type { TeamSummary } from './models';

export interface Fixture {
  round: number;
  contract_id: number;
  host: TeamSummary;
  guest: TeamSummary;
  kickoff_at: string;
  status: 'NEGOTIATING' | 'SIGNED' | 'CANCELLED';
  result: string | null;
}

export interface Standing {
  team_id: number;
  name: string;
  played: number;
  won: number;
  drawn: number;
  lost: number;
  goals_for: number;
  goals_against: number;
  goal_difference: number;
  points: number;
}

export interface Season {
  calendar: Fixture[];
  table: Standing[];
}

export interface RefereeMatch {
  assignment_id: number;
  contract_id: number;
  status: 'PENDING' | 'ACCEPTED';
  league_name: string;
  host_name: string;
  guest_name: string;
  kickoff_at: string;
  place_kind: 'VENUE' | 'INFORMAL' | 'TO_AGREE';
  place_note: string | null;
  result_status: 'PENDING' | 'CONFIRMED' | 'DISPUTED' | null;
  host_score: number | null;
  guest_score: number | null;
}

/** Fechas agrupadas para pintarlas: [[fecha 1...], [fecha 2...]]. */
export function groupByRound(calendar: Fixture[]): { round: number; matches: Fixture[] }[] {
  const rounds = new Map<number, Fixture[]>();
  for (const f of calendar) rounds.set(f.round, [...(rounds.get(f.round) ?? []), f]);
  return [...rounds.entries()].sort(([a], [b]) => a - b).map(([round, matches]) => ({ round, matches }));
}

/** El árbitro puede fijar el resultado si aceptó, ya pasó la hora y no está confirmado. */
export function canRefereeReport(match: RefereeMatch, now: Date): boolean {
  return (
    match.status === 'ACCEPTED' &&
    now.getTime() >= Date.parse(match.kickoff_at) &&
    match.result_status !== 'CONFIRMED'
  );
}
