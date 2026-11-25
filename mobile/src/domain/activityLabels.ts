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
  BOOKING_REQUESTED: 'Pidió reservar la cancha',
  BOOKING_CONFIRMED: 'El establecimiento confirmó la cancha',
  BOOKING_REJECTED: 'El establecimiento rechazó la reserva',
  BOOKING_CANCELLED: 'Canceló la reserva de cancha',
  LINEUP_RECORDED: 'Registró la planilla del partido',
  COINS_MOVED: 'Movimiento de monedas RIVAL',
  TRANSFER_LISTED: 'Puso a un jugador en el mercado',
  TRANSFER_UNLISTED: 'Quitó a un jugador del mercado',
  TRANSFER_OFFERED: 'Hizo una oferta de traspaso',
  TRANSFER_OWNER_ACCEPTED: 'El DT dueño aceptó la oferta de traspaso',
  TRANSFER_OWNER_REJECTED: 'El DT dueño rechazó la oferta de traspaso',
  TRANSFER_PLAYER_REJECTED: 'El jugador rechazó su traspaso',
  TRANSFER_WITHDRAWN: 'Retiró la oferta de traspaso',
  TRANSFER_COMPLETED: 'Traspaso completado con la aceptación del jugador',
  LEAGUE_FIXTURE_GENERATED: 'Armó el calendario de la liga',
  REFEREE_ASSIGNED: 'Asignó árbitro al partido',
  REFEREE_ACCEPTED: 'El árbitro aceptó el partido',
  REFEREE_DECLINED: 'El árbitro rechazó el partido',
  RESULT_SET_BY_REFEREE: 'El árbitro fijó el resultado',
  TEAM_RATINGS_UPDATED: 'Se actualizó el nivel de los equipos',
  CALLUP_SENT: 'Envió la convocatoria',
  CALLUP_RESPONDED: 'Respondió a la convocatoria',
  PLAYER_RATED: 'Valoró a un compañero',
  TEAM_BLOCKED: 'Bloqueó a un equipo',
  TEAM_UNBLOCKED: 'Desbloqueó a un equipo',
  LOAN_REQUESTED: 'Pidió un jugador prestado para el partido',
  LOAN_OWNER_ACCEPTED: 'El DT dueño aceptó prestar al jugador',
  LOAN_OWNER_REJECTED: 'El DT dueño rechazó el préstamo',
  LOAN_ACTIVE: 'El jugador aceptó jugar prestado',
  LOAN_PLAYER_REJECTED: 'El jugador rechazó el préstamo',
  LOAN_CANCELLED: 'Canceló el préstamo',
  TRANSFER_WINDOW_SET: 'Cambió la ventana de traspasos de la liga',
  CHAT_MESSAGE_DELETED: 'Borró un mensaje del chat',
  CHECKED_IN: 'Hizo check-in en la cancha',
  CUP_CREATED: 'Armó la copa de la liga',
  CUP_TEAM_ADVANCED: 'Un equipo pasó de ronda en la copa',
  CUP_TIEBREAK_SET: 'Definió un empate de copa por penales',
  CUP_CHAMPION: 'Hay campeón de la copa',
  VENUE_LOCATION_SET: 'Guardó la ubicación del establecimiento',
  CHAT_READ_BY_MODERATOR: 'Una persona moderadora revisó el chat por un reporte',
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
  balance: 'saldo',
  amount: 'monedas',
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
