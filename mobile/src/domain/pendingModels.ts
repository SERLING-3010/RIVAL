// Pendientes del usuario (Sprint 11): lo que espera su acción, calculado por el backend.

export type PendingTarget = 'contract' | 'team' | 'league' | 'venue' | 'transfers' | 'referee' | 'loans';

export interface PendingItem {
  kind: string;
  title: string;
  detail: string;
  target: PendingTarget;
  target_id: number | null;
  due_at: string | null;
}

const URGENT = new Set([
  'SIGN_CONTRACT',
  'REPORT_RESULT',
  'RESULT_DISPUTED',
  'CALLUP',
  'REFEREE_RESULT',
  'CONFIRM_GOAL_KINDS', // Sprint 23: vence a las 72 horas
]);

/** Insignia corta: "Urgente" si tiene hora en las próximas 24 h o es de un partido ya jugado. */
export function urgency(item: PendingItem, now: Date): string | undefined {
  if (!item.due_at) return undefined;
  const hours = (Date.parse(item.due_at) - now.getTime()) / 3_600_000;
  return URGENT.has(item.kind) && hours <= 24 ? 'Urgente' : undefined;
}

/** Texto de la tarjeta del inicio: "Pendientes (3)" o "Sin pendientes". */
export function pendingCardTitle(count: number | null): string {
  if (count === null) return 'Pendientes';
  return count === 0 ? 'Sin pendientes' : `Pendientes (${count})`;
}
