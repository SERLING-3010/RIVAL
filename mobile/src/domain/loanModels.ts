// Préstamos por un partido y ventanas de traspasos (Sprint 13).

import { parseLocalDateTime } from './dateTime.ts';

export type LoanStatus = 'PENDING_OWNER' | 'PENDING_PLAYER' | 'ACTIVE' | 'REJECTED' | 'CANCELLED';

export interface Loan {
  id: number;
  contract_id: number;
  player_id: number;
  player_name: string;
  from_team: string;
  to_team: string;
  status: LoanStatus;
  kickoff_at: string;
}

export const LOAN_STATUS_LABEL: Record<LoanStatus, string> = {
  PENDING_OWNER: 'Espera al DT del equipo dueño',
  PENDING_PLAYER: 'Espera al jugador',
  ACTIVE: 'Préstamo activo',
  REJECTED: 'Rechazado',
  CANCELLED: 'Cancelado',
};

/** Texto de la ventana de traspasos de una liga en un momento dado. */
export function windowText(
  start: string | null,
  end: string | null,
  now: Date,
  fmt: (iso: string) => string,
): string {
  if (start === null || end === null) return 'Sin ventana: los traspasos están abiertos.';
  const t = now.getTime();
  if (t < Date.parse(start)) return `Ventana cerrada. Abre el ${fmt(start)}.`;
  if (t < Date.parse(end)) return `Ventana abierta hasta el ${fmt(end)}.`;
  return `Ventana cerrada desde el ${fmt(end)}.`;
}

export type WindowForm = { ok: true; start: string; end: string } | { ok: false; error: string };

/** Valida las fechas escritas (dd/mm/aaaa hh:mm) de una ventana de traspasos. */
export function parseWindow(startText: string, endText: string): WindowForm {
  const start = parseLocalDateTime(startText);
  const end = parseLocalDateTime(endText);
  if (start === null || end === null)
    return { ok: false, error: 'Escribe las fechas como dd/mm/aaaa hh:mm.' };
  if (Date.parse(end) <= Date.parse(start))
    return { ok: false, error: 'El cierre debe ser después de la apertura.' };
  return { ok: true, start, end };
}

/** Solo se presta a un jugador (no DT ni capitán) que aún no tenga préstamo en el partido. */
export function borrowable<M extends { role: string; user_id: number }>(members: M[], taken: number[]): M[] {
  return members.filter((m) => m.role === 'PLAYER' && !taken.includes(m.user_id));
}
