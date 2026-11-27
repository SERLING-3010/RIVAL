// Día del partido (Sprint 10): convocatoria, valoraciones y nivel Glicko-2 del equipo.

export type CallUpStatus = 'INVITED' | 'GOING' | 'NOT_GOING';

export interface CallUpItem {
  user_id: number;
  display_name: string;
  status: CallUpStatus;
}

export interface TeamCallUp {
  contract_id: number;
  items: CallUpItem[];
  going: number;
  not_going: number;
  pending: number;
}

export interface MyCallUp {
  contract_id: number;
  my_team: string;
  opponent: string;
  kickoff_at: string;
  status: CallUpStatus;
}

export interface Rateable {
  user_id: number;
  display_name: string;
}

export const CALLUP_STATUS_LABEL: Record<CallUpStatus, string> = {
  INVITED: 'Sin responder',
  GOING: 'Va',
  NOT_GOING: 'No va',
};

/** "Nivel 1.612 (confiable)" o "Nivel 1.540 (aún incierto)"; sin partidos confirmados: "Sin nivel aún". */
export function levelText(level: number | null, reliable: boolean): string {
  if (level === null) return 'Sin nivel aún';
  const grouped = String(level).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  return `Nivel ${grouped} (${reliable ? 'confiable' : 'aún incierto'})`;
}

/** El nivel es confiable cuando su incertidumbre (RD de Glicko-2) es baja. Igual que el backend. */
export const RELIABLE_RD = 100;

export function parseScore(text: string): number | null {
  return /^(10|[1-9])$/.test(text.trim()) ? Number(text) : null;
}
