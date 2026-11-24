// Ligas y cuerpo arbitral (Sprint 5).

import type { TeamSummary } from './models';

export type StaffRole = 'ORGANIZER' | 'CO_ORGANIZER' | 'REFEREE_COORDINATOR';
export type EntryStatus = 'PENDING' | 'APPROVED' | 'REJECTED' | 'WITHDRAWN';
export type EntryKind = 'team' | 'referee';

export interface LeagueSummary {
  id: number;
  name: string;
  sport_code: string;
  modality_code: string;
  city: string;
  season: string;
  team_count: number;
  referee_count: number;
}

export interface LeaguePage {
  items: LeagueSummary[];
  page: number;
  page_size: number;
  total: number;
}

export interface StaffMember {
  user_id: number;
  display_name: string;
  role: StaffRole;
}

export interface TeamEntry {
  id: number;
  team: TeamSummary;
  status: EntryStatus;
}

export interface RefereeEntry {
  id: number;
  user_id: number;
  display_name: string;
  status: EntryStatus;
}

export interface LeagueDetail {
  league: LeagueSummary;
  description: string | null;
  my_role: StaffRole | null;
  transfer_window_start: string | null;
  transfer_window_end: string | null;
  staff: StaffMember[];
  teams: TeamEntry[];
  referees: RefereeEntry[];
  pending_teams: TeamEntry[];
  pending_referees: RefereeEntry[];
  my_team_requests: TeamEntry[];
  my_referee_request: RefereeEntry | null;
}

export interface MyLeague {
  league: LeagueSummary;
  relation: StaffRole | 'REFEREE' | 'TEAM';
}

export interface CreateLeaguePayload {
  name: string;
  sport_code: string;
  modality_code: string;
  city: string;
  season: string;
  description: string | null;
}
