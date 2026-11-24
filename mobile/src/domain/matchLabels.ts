import type { DistanceBand, MatchRequest, Offer, PlaceKind, RefereeMode, SearchScope } from './matchModels';

export const SCOPE_LABEL: Record<SearchScope, string> = {
  NEARBY: 'Cerca de mí',
  NEIGHBORHOOD: 'Mi barrio',
  CITY: 'Mi ciudad',
};

// Solo rangos: nunca la ubicación exacta de nadie.
export const DISTANCE_LABEL: Record<DistanceBand, string> = {
  UNDER_2_KM: 'a menos de 2 km',
  FROM_2_TO_5_KM: 'a 2–5 km',
  OVER_5_KM: 'a más de 5 km',
};

export const REFEREE_LABEL: Record<RefereeMode, string> = {
  WITH: 'Con árbitro',
  WITHOUT: 'Sin árbitro',
  EITHER: 'Con o sin árbitro',
};

export const PLACE_LABEL: Record<PlaceKind, string> = {
  VENUE: 'Cancha de establecimiento',
  INFORMAL: 'Lugar informal (parque, cancha de barrio)',
  TO_AGREE: 'Lugar por acordar',
};

export const REQUEST_STATUS_LABEL: Record<MatchRequest['status'], string> = {
  OPEN: 'Buscando rival',
  MATCHED: 'Rival encontrado',
  CANCELLED: 'Cancelada',
  EXPIRED: 'Venció',
};

export const OFFER_STATUS_LABEL: Record<Offer['status'], string> = {
  PENDING: 'Pendiente',
  ACCEPTED: 'Aceptada',
  REJECTED: 'Rechazada',
  WITHDRAWN: 'Retirada',
  SUPERSEDED: 'Reemplazada',
  CANCELLED: 'Cancelada',
};

export function distanceText(band: DistanceBand | null): string {
  return band ? DISTANCE_LABEL[band] : '';
}
