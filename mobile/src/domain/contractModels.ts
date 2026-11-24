// Contrato del partido (Sprint 3): versiones inmutables y firmas de los dos administradores.

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
}

export interface ContractSummary {
  id: number;
  host: TeamSummary;
  guest: TeamSummary;
  status: ContractStatus;
  kickoff_at: string;
  my_side: Side;
  awaiting_my_signature: boolean;
}
