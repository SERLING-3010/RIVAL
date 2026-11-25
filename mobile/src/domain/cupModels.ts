// Copa eliminatoria de una liga (Sprint 16): cuadro por rondas, pases directos y penales.

import { parseLocalDateTime } from './dateTime.ts';

export interface CupMatch {
  id: number;
  position: number;
  host_team_id: number | null;
  guest_team_id: number | null;
  host_name: string | null;
  guest_name: string | null;
  contract_id: number | null;
  host_score: number | null;
  guest_score: number | null;
  winner_name: string | null;
  needs_tiebreak: boolean;
}

export interface CupRound {
  number: number;
  name: string;
  planned_at: string;
  matches: CupMatch[];
}

export interface Cup {
  league_id: number;
  champion_name: string | null;
  can_manage: boolean;
  rounds: CupRound[];
}

/** Texto del cruce: "Águilas 2 – 1 Bravos", "Águilas (pasa directo)" o "Por definir". */
export function matchLine(m: CupMatch, firstRound: boolean): string {
  const host = m.host_name ?? 'Por definir';
  if (m.guest_name === null)
    return firstRound && m.host_name ? `${host} (pasa directo)` : `${host} vs Por definir`;
  if (m.host_score === null || m.guest_score === null) return `${host} vs ${m.guest_name}`;
  return `${host} ${m.host_score} – ${m.guest_score} ${m.guest_name}`;
}

export type Schedule = { ok: true; first: string; days: number } | { ok: false; error: string };

/** Valida la primera fecha (dd/mm/aaaa hh:mm) y los días entre rondas (1 a 14). */
export function parseSchedule(firstText: string, daysText: string): Schedule {
  const first = parseLocalDateTime(firstText);
  const days = /^\d{1,2}$/.test(daysText.trim()) ? Number(daysText) : 0;
  if (first === null) return { ok: false, error: 'Escribe la primera fecha como dd/mm/aaaa hh:mm.' };
  if (days < 1 || days > 14) return { ok: false, error: 'Entre rondas deben pasar de 1 a 14 días.' };
  return { ok: true, first, days };
}
