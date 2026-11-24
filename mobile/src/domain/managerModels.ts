// Modo manager (Sprint 7): fichas, monedas RIVAL y mercado de fichajes.

import type { TeamSummary } from './models';

export type TransferStatus =
  'PENDING_OWNER' | 'PENDING_PLAYER' | 'COMPLETED' | 'REJECTED' | 'WITHDRAWN' | 'CANCELLED';

export interface PlayerCard {
  user_id: number;
  display_name: string;
  position: string | null;
  sports: string[];
  teams: TeamSummary[];
  matches: number;
  goals: number;
  wins: number;
  draws: number;
  losses: number;
  rating_average: number | null;
  rating_votes: number;
}

export interface MarketItem {
  player_id: number;
  display_name: string;
  position: string | null;
  team: TeamSummary;
  matches: number;
  goals: number;
}

export interface TransferOffer {
  id: number;
  player_id: number;
  player_name: string;
  from_team: TeamSummary;
  to_team: TeamSummary;
  amount: number;
  status: TransferStatus;
  created_at: string;
}

export interface CoinEntry {
  amount: number;
  reason: string;
  reference: string | null;
  created_at: string;
}

export interface SquadMember {
  user_id: number;
  display_name: string;
  role: 'COACH' | 'CAPTAIN' | 'PLAYER';
  position: string | null;
  listed: boolean;
  matches: number;
  goals: number;
}

export interface TeamManager {
  team: TeamSummary;
  is_admin: boolean;
  balance: number;
  level: number | null;
  level_rd: number | null;
  level_matches: number;
  history: CoinEntry[];
  squad: SquadMember[];
  offers_received: TransferOffer[];
  offers_sent: TransferOffer[];
}
