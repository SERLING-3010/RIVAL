// Central de actividad (Sprint 4): traduce los eventos de auditoría a frases para personas.

export interface ActivityItem {
  occurred_at: string;
  action: string;
  entity: string;
  entity_id: string;
  actor_type: string;
  actor_name: string | null;
  approver_name: string | null;
  before: Record<string, unknown> | null;
  after: Record<string, unknown> | null;
}

const ACTION_LABEL: Record<string, string> = {
  TEAM_CREATED: 'Creó el equipo',
  TEAM_ADMIN_CHANGED: 'Cambió el administrador del equipo',
  CAPTAIN_SET: 'Nombró capitán',
  MEMBER_LEFT: 'Salió del equipo',
  JOIN_REQUESTED: 'Pidió unirse al equipo',
  JOIN_APPROVED: 'Aprobó una solicitud para unirse',
  PLAYER_INVITED: 'Invitó a un jugador',
  INVITATION_ACCEPTED: 'Aceptó la invitación',
  MATCH_REQUEST_CREATED: 'Publicó una búsqueda de partido',
  MATCH_REQUEST_CANCELLED: 'Canceló una búsqueda de partido',
  MATCH_OFFER_MADE: 'Hizo una oferta',
  MATCH_OFFER_ACCEPTED: 'Aceptó una oferta',
  MATCH_OFFER_REJECTED: 'Rechazó una oferta',
  MATCH_OFFER_WITHDRAWN: 'Retiró una oferta',
  CONTRACT_CREATED: 'Se creó el contrato del partido',
  CONTRACT_VERSION_PROPOSED: 'Propuso cambios al contrato',
  CONTRACT_SIGNED: 'Firmó el contrato',
  CONTRACT_AMENDMENT_REJECTED: 'Rechazó un cambio al contrato',
  CONTRACT_AMENDMENT_WITHDRAWN: 'Retiró su cambio al contrato',
  CONTRACT_CANCELLED: 'Canceló el partido',
  RESULT_REPORTED: 'Reportó el marcador',
  RESULT_CONFIRMED: 'Reportó el marcador y quedó confirmado',
  RESULT_DISPUTED: 'Reportó un marcador distinto: partido en disputa',
  LEAGUE_TEAM_REQUESTED: 'Pidió inscribir al equipo en una liga',
  LEAGUE_TEAM_APPROVED: 'Aprobó la inscripción del equipo en la liga',
  LEAGUE_TEAM_REJECTED: 'Rechazó la inscripción del equipo en la liga',
  LEAGUE_TEAM_WITHDRAWN: 'Retiró al equipo de la liga',
};

const FIELD_LABEL: Record<string, string> = {
  kickoff_at: 'hora',
  duration_minutes: 'duración',
  referee_mode: 'árbitro',
  place_kind: 'lugar',
  place_note: 'detalle del lugar',
  host_kit_color: 'uniforme local',
  guest_kit_color: 'uniforme visitante',
  substitutions: 'cambios',
  field_cost_split: 'pago de cancha',
  referee_cost_split: 'pago de árbitro',
  cancellation_notice_hours: 'aviso para cancelar',
  host_score: 'goles local',
  guest_score: 'goles visitante',
  reason: 'motivo',
  status: 'estado',
};

export function actionLabel(action: string): string {
  return ACTION_LABEL[action] ?? action;
}

export function actorText(item: ActivityItem): string {
  if (item.actor_name) return item.actor_name;
  return item.actor_type === 'SYSTEM_RULE' ? 'RIVAL (regla automática)' : 'Sistema';
}

const show = (value: unknown): string => (value === null || value === undefined ? '—' : String(value));

/** Líneas "campo: antes → después" solo para los campos conocidos que cambiaron o se fijaron. */
export function changeLines(item: ActivityItem): string[] {
  const after = item.after ?? {};
  return Object.keys(after)
    .filter((key) => key in FIELD_LABEL)
    .map((key) => {
      const label = FIELD_LABEL[key] ?? key;
      const before = item.before?.[key];
      return before === undefined
        ? `${label}: ${show(after[key])}`
        : `${label}: ${show(before)} → ${show(after[key])}`;
    });
}
