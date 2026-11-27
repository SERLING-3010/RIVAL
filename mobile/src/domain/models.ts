// Contratos de datos con la API de RIVAL (backend/app/api/schemas_*.py).

export type UserRole = 'PLAYER' | 'COACH' | 'REFEREE' | 'VENUE_OWNER';
export type TeamRole = 'COACH' | 'CAPTAIN' | 'PLAYER';

export interface Modality {
  code: string;
  name: string;
  players_per_side: number;
}

export interface Sport {
  code: string;
  name: string;
  modalities: Modality[];
}

export interface User {
  id: number;
  email: string;
  display_name: string;
  roles: UserRole[];
  sports: string[];
  city: string;
  neighborhood: string;
  position: string | null;
  needs_terms?: boolean; // Sprint 27: debe aceptar la versión vigente
}

export interface SessionResponse {
  token: string;
  user: User;
}

export interface RegisterPayload {
  email: string;
  password: string;
  display_name: string;
  birth_date: string;
  role: UserRole;
  sports: string[];
  city: string;
  neighborhood: string;
  position: string | null;
  accept_terms: boolean; // Sprint 27
}

export interface TeamSummary {
  id: number;
  name: string;
  sport_code: string;
  modality_code: string;
  city: string;
  neighborhood: string;
  member_count: number;
  has_coach: boolean;
}

export interface Member {
  user_id: number;
  display_name: string;
  role: TeamRole;
  position: string | null;
}

export interface TeamDetail {
  team: TeamSummary;
  admin_user_id: number | null;
  members: Member[];
}

export interface MyTeam {
  team: TeamSummary;
  my_role: TeamRole;
  is_admin: boolean;
  pending_requests: number;
}

export interface TeamPage {
  items: TeamSummary[];
  page: number;
  page_size: number;
  total: number;
}

export interface JoinRequest {
  id: number;
  team_id: number;
  user_id: number;
  display_name: string;
  position: string | null;
  desired_role: TeamRole;
  message: string | null;
  status: string;
}

export interface CreateTeamPayload {
  name: string;
  sport_code: string;
  modality_code: string;
  city: string;
  neighborhood: string;
  as_coach: boolean;
}

export interface TeamSearchQuery {
  sport?: string;
  city?: string;
  q?: string;
  page?: number;
}
