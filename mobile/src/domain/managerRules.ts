// Reglas locales del modo manager. Las monedas RIVAL son virtuales: no se compran ni se venden.

import type { SquadMember, TransferStatus } from './managerModels';

export const TRANSFER_STATUS_LABEL: Record<TransferStatus, string> = {
  PENDING_OWNER: 'Espera al DT del equipo dueño',
  PENDING_PLAYER: 'Espera la respuesta del jugador',
  COMPLETED: 'Traspaso completado',
  REJECTED: 'Rechazada',
  WITHDRAWN: 'Retirada',
  CANCELLED: 'Cancelada',
};

const REASON_LABEL: Record<string, string> = {
  STARTING_BUDGET: 'Presupuesto inicial',
  MATCH_REWARD: 'Premio por partido confirmado',
  TRANSFER_PAID: 'Pago por fichaje',
  TRANSFER_RECEIVED: 'Venta de jugador',
};

export function coinReason(reason: string): string {
  return REASON_LABEL[reason] ?? reason;
}

/** 1250 → "1.250 RC" (monedas RIVAL, enteros). */
export function formatCoins(amount: number): string {
  const sign = amount < 0 ? '−' : '';
  return `${sign}${String(Math.abs(amount)).replace(/\B(?=(\d{3})+(?!\d))/g, '.')} RC`;
}

export function parseOffer(
  text: string,
  balance: number,
): { ok: true; amount: number } | { ok: false; error: string } {
  const clean = text.trim().replace(/\./g, '');
  if (!/^\d{1,7}$/.test(clean) || Number(clean) < 1 || Number(clean) > 1_000_000) {
    return { ok: false, error: 'La oferta va de 1 a 1.000.000 monedas RIVAL.' };
  }
  const amount = Number(clean);
  if (amount > balance) return { ok: false, error: `Tu equipo tiene ${formatCoins(balance)}.` };
  return { ok: true, amount };
}

export function canBeListed(member: SquadMember): boolean {
  return member.role === 'PLAYER';
}

export type LineupResult =
  { ok: true; players: { user_id: number; goals: number }[] } | { ok: false; error: string };

/** played: ids marcados; goals: texto por jugador. La suma de goles no supera el marcador del equipo. */
export function lineupFromForm(
  played: number[],
  goals: Record<number, string>,
  teamScore: number,
): LineupResult {
  if (played.length === 0) return { ok: false, error: 'Marca al menos un jugador que jugó el partido.' };
  const players = [];
  for (const id of played) {
    const text = (goals[id] ?? '').trim() || '0';
    if (!/^\d{1,3}$/.test(text))
      return { ok: false, error: 'Los goles de cada jugador son un número de 0 a 999.' };
    players.push({ user_id: id, goals: Number(text) });
  }
  if (players.reduce((sum, p) => sum + p.goals, 0) > teamScore) {
    return { ok: false, error: `La suma de goles supera el marcador de tu equipo (${teamScore}).` };
  }
  return { ok: true, players };
}
