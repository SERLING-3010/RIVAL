// Contratos del Sprint 2: rivales, agentes libres, invitaciones, búsquedas de partido y ofertas.

import type { TeamSummary } from './models';

export type SearchScope = 'NEARBY' | 'NEIGHBORHOOD' | 'CITY';
export type DistanceBand = 'UNDER_2_KM' | 'FROM_2_TO_5_KM' | 'OVER_5_KM';
export type RefereeMode = 'WITH' | 'WITHOUT' | 'EITHER';
export type PlaceKind = 'VENUE' | 'INFORMAL' | 'TO_AGREE';

export interface Rival {
  team: TeamSummary;
  distance_band: DistanceBand | null;
  level: number | null; // nivel Glicko-2 (Sprint 10)
  level_reliable: boolean;
}

export interface RivalPage {
  items: Rival[];
  page: number;
  page_size: number;
  total: number;
}

export interface FreeAgentProfile {
  sport_code: string;
  active: boolean;
  position: string | null;
  note: string | null;
}

export interface FreeAgent {
  user_id: number;
  display_name: string;
  sport_code: string;
  position: string | null;
  note: string | null;
  neighborhood: string;
  city: string;
}

export interface FreeAgentPage {
  items: FreeAgent[];
  page: number;
  page_size: number;
  total: number;
}

export interface Invitation {
  id: number;
  team: TeamSummary;
  message: string | null;
}

export interface MatchRequest {
  id: number;
  team: TeamSummary;
  target_team_id: number | null;
  scope: SearchScope;
  radius_km: number | null;
  window_start: string;
  window_end: string;
  referee_mode: RefereeMode;
  place_kind: PlaceKind;
  place_note: string | null;
  message: string | null;
  status: 'OPEN' | 'MATCHED' | 'CANCELLED' | 'EXPIRED';
  distance_band: DistanceBand | null;
  pending_offers: number;
  accepted_offer_id: number | null;
}

export interface Offer {
  id: number;
  request_id: number;
  team: TeamSummary;
  version: number;
  proposed_start: string;
  referee_mode: RefereeMode;
  place_kind: PlaceKind;
  place_note: string | null;
  message: string | null;
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED' | 'WITHDRAWN' | 'SUPERSEDED' | 'CANCELLED';
}

export interface MatchRequestPayload {
  window_start: string;
  window_end: string;
  scope: SearchScope;
  radius_km: number | null;
  target_team_id: number | null;
  referee_mode: RefereeMode;
  place_kind: PlaceKind;
  place_note: string | null;
  message: string | null;
}

export interface OfferPayload {
  proposed_start: string;
  referee_mode: Exclude<RefereeMode, 'EITHER'>;
  place_kind: PlaceKind;
  place_note: string | null;
  message: string | null;
}
