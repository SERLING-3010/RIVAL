// Rivales sugeridos con sus motivos (Sprint 18). La cercanía llega solo por rangos.

import type { DistanceBand } from './matchModels';
import type { TeamSummary } from './models';

export interface Suggestion {
  team: TeamSummary;
  distance_band: DistanceBand | null;
  level: number | null;
  reasons: string[];
}

/** "Barrio Dos · Nivel 1520" o "Barrio Dos · Sin nivel aún". */
export function suggestionSubtitle(s: Suggestion): string {
  return `${s.team.neighborhood} · ${s.level === null ? 'Sin nivel aún' : `Nivel ${s.level}`}`;
}
