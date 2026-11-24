// Qué puede hacer cada administrador con el contrato. El backend vuelve a validar todo.

import type {
  Contract,
  ContractStatus,
  ContractTerms,
  CostSplit,
  ResultStatus,
  Side,
} from './contractModels';

export const CONTRACT_STATUS_LABEL: Record<ContractStatus, string> = {
  NEGOTIATING: 'En negociación',
  SIGNED: 'Firmado por ambos',
  CANCELLED: 'Cancelado',
};

export const COST_SPLIT_LABEL: Record<CostSplit, string> = {
  HALF: 'Mitad y mitad',
  HOST: 'Lo paga el local',
  GUEST: 'Lo paga el visitante',
};

export const RESULT_STATUS_LABEL: Record<ResultStatus, string> = {
  PENDING: 'Falta el reporte del rival',
  CONFIRMED: 'Resultado confirmado',
  DISPUTED: 'En disputa: los marcadores no coinciden',
};

export interface ContractActions {
  canSign: boolean;
  canPropose: boolean;
  canRejectAmendment: boolean;
  canCancel: boolean;
  canReportResult: boolean;
  /** Mensaje corto sobre a quién le toca. */
  status: string;
}

export function otherSide(side: Side): Side {
  return side === 'HOST' ? 'GUEST' : 'HOST';
}

/** Hora de inicio que cuenta: la de la versión firmada; si no hay, la de la versión en negociación. */
export function effectiveKickoff(contract: Contract): number {
  return Date.parse((contract.signed ?? contract.current).terms.kickoff_at);
}

export function contractActions(contract: Contract, now: Date = new Date()): ContractActions {
  const open = contract.status !== 'CANCELLED';
  const started = now.getTime() >= effectiveKickoff(contract);
  const admin = contract.is_admin && open;
  const changeable = admin && !started;
  const iSigned = contract.current.signed_by.includes(contract.my_side);
  const negotiating = contract.status === 'NEGOTIATING';
  const amendment = negotiating && contract.signed !== null;
  let status = CONTRACT_STATUS_LABEL[contract.status];
  if (negotiating) {
    status = iSigned ? 'Esperando la firma del rival.' : 'Falta la firma de tu equipo.';
  }
  if (amendment) {
    status += ' Mientras tanto vale la versión firmada.';
  }
  return {
    canSign: changeable && negotiating && !iSigned,
    canPropose: changeable,
    canRejectAmendment: admin && amendment,
    canCancel: changeable,
    canReportResult: admin && started && contract.signed !== null && contract.result?.status !== 'CONFIRMED',
    status,
  };
}

/** Lista legible de condiciones para mostrar en la pantalla del contrato. */
export function describeTerms(terms: ContractTerms, hostName: string, guestName: string): string[] {
  const lines = [
    `Duración: ${terms.duration_minutes} min`,
    `Uniformes: ${hostName} ${terms.host_kit_color}, ${guestName} ${terms.guest_kit_color}`,
    `Cambios: ${terms.substitutions === null ? 'ilimitados' : terms.substitutions}`,
    `Cancha: ${COST_SPLIT_LABEL[terms.field_cost_split]}`,
    `Aviso para cancelar: ${terms.cancellation_notice_hours} h antes`,
  ];
  if (terms.referee_mode === 'WITH') {
    lines.push(`Árbitro: ${COST_SPLIT_LABEL[terms.referee_cost_split]}`);
  } else if (terms.foul_caller_note) {
    lines.push(`Faltas dudosas: ${terms.foul_caller_note}`);
  }
  if (terms.extra_rules) lines.push(`Reglas extra: ${terms.extra_rules}`);
  return lines;
}

/** Nombres de los campos que cambian entre dos versiones (para resaltar la propuesta). */
export function changedFields(before: ContractTerms, after: ContractTerms): (keyof ContractTerms)[] {
  return (Object.keys(after) as (keyof ContractTerms)[]).filter((key) => before[key] !== after[key]);
}
