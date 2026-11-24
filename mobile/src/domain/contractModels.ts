// Contrato del partido (Sprint 3) y resultado (Sprint 4): versiones inmutables, firmas y marcador.

import type { PlaceKind, RefereeMode } from './matchModels';
import type { TeamSummary } from './models';

export type ContractStatus = 'NEGOTIATING' | 'SIGNED' | 'CANCELLED';
export type CostSplit = 'HALF' | 'HOST' | 'GUEST';
export type Side = 'HOST' | 'GUEST';

export interface ContractTerms {
  kickoff_at: string;
  duration_minutes: number;
  referee_mode: Exclude<RefereeMode, 'EITHER'>;
  place_kind: PlaceKind;
  place_note: string | null;
  host_kit_color: string;
  guest_kit_color: string;
  substitutions: number | null;
  field_cost_split: CostSplit;
  referee_cost_split: CostSplit;
  cancellation_notice_hours: number;
  foul_caller_note: string | null;
  extra_rules: string | null;
}

export interface ContractVersion {
  version: number;
  terms: ContractTerms;
  proposed_by_side: Side | null;
  note: string | null;
  created_at: string;
  signed_by: Side[];
}

export type ResultStatus = 'PENDING' | 'CONFIRMED' | 'DISPUTED';

export interface ResultReport {
  side: Side;
  host_score: number;
  guest_score: number;
  reported_at: string;
}

export interface MatchResult {
  status: ResultStatus;
  host_score: number | null;
  guest_score: number | null;
  reports: ResultReport[];
}

export interface Contract {
  id: number;
  request_id: number;
  host: TeamSummary;
  guest: TeamSummary;
  status: ContractStatus;
  my_side: Side;
  is_admin: boolean;
  current: ContractVersion;
  signed: ContractVersion | null;
  versions: ContractVersion[];
  cancel_reason: string | null;
  result: MatchResult | null;
}

export interface ContractSummary {
  id: number;
  host: TeamSummary;
  guest: TeamSummary;
  status: ContractStatus;
  kickoff_at: string;
  my_side: Side;
  awaiting_my_signature: boolean;
  result_status: ResultStatus | null;
  host_score: number | null;
  guest_score: number | null;
}
