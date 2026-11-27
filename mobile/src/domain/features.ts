// Alcance del lanzamiento (Sprint 29): lo decide el backend (`GET /api/v1/features`).
// Decisión del dueño: lanzar solo con fútbol, sin árbitros y sin establecimientos deportivos.

import type { RoleOption } from './labels';
import type { PlaceKind, RefereeMode } from './matchModels';

export interface Features {
  sports: string[];
  referees: boolean;
  venues: boolean;
}

/** Mientras no se sepa (o sin red), se muestra todo: el backend igual rechaza lo apagado. */
export const ALL_FEATURES: Features = { sports: [], referees: true, venues: true };

export function roleOptions(options: RoleOption[], f: Features): RoleOption[] {
  return options.filter(
    (o) => (o.role !== 'REFEREE' || f.referees) && (o.role !== 'VENUE_OWNER' || f.venues),
  );
}

/** Sin árbitros, la única opción es «sin árbitro»: el selector ni se muestra. */
export function refereeChoices<T extends RefereeMode>(choices: T[], f: Features): T[] {
  return f.referees ? choices : choices.filter((c) => c === 'WITHOUT');
}

export function placeChoices(choices: PlaceKind[], f: Features): PlaceKind[] {
  return f.venues ? choices : choices.filter((c) => c !== 'VENUE');
}
