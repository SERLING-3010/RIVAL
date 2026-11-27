// Goles con tipo (Sprint 23): se marcan en la planilla y cuentan para las hazañas cuando el rival confirma.

export const GOAL_KINDS = ['CABEZA', 'PENAL', 'TIRO_LIBRE', 'CHILENA', 'OLIMPICO'] as const;
export type GoalKind = (typeof GOAL_KINDS)[number];

export const GOAL_KIND_LABEL: Record<GoalKind, string> = {
  CABEZA: 'De cabeza',
  PENAL: 'Penal',
  TIRO_LIBRE: 'Tiro libre',
  CHILENA: 'Chilena',
  OLIMPICO: 'Olímpico',
};

export type GoalClaimStatus = 'PENDING' | 'CONFIRMED' | 'REJECTED' | 'EXPIRED';

export interface GoalClaim {
  id: number;
  team_id: number;
  user_id: number;
  display_name: string;
  kind: GoalKind;
  status: GoalClaimStatus;
  claimed_at: string;
  can_decide: boolean;
}

export const CLAIM_STATUS_LABEL: Record<GoalClaimStatus, string> = {
  PENDING: 'Esperando al rival',
  CONFIRMED: 'Confirmado por el rival',
  REJECTED: 'Rechazado: cuenta como gol normal',
  EXPIRED: 'Sin respuesta en 72 horas: cuenta como gol normal',
};

/** Agrega un tipo si aún hay goles sin tipo para ese jugador. */
export function addKind(marked: GoalKind[], kind: GoalKind, goals: number): GoalKind[] {
  return marked.length < goals ? [...marked, kind] : marked;
}

export function removeKindAt(marked: GoalKind[], index: number): GoalKind[] {
  return marked.filter((_, i) => i !== index);
}
