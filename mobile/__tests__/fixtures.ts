// Datos de prueba para los componentes [SIMULACIÓN].
import { jest } from '@jest/globals';

import type { Action } from '../src/controllers/useAction';
import type { ContractController } from '../src/controllers/useContracts';
import type { Contract, ContractTerms, ContractVersion } from '../src/domain/contractModels';
import type { TeamSummary } from '../src/domain/models';

export const team = (id: number, name: string): TeamSummary => ({
  id,
  name,
  sport_code: 'FOOTBALL',
  modality_code: 'F7',
  city: 'Barranquilla',
  neighborhood: 'El Prado',
  member_count: 7,
  has_coach: true,
});

export const terms: ContractTerms = {
  // Siempre en el futuro respecto al día en que corren las pruebas.
  kickoff_at: new Date(Date.now() + 2 * 86_400_000).toISOString(),
  duration_minutes: 60,
  referee_mode: 'WITHOUT',
  place_kind: 'INFORMAL',
  place_note: 'Parque Sagrado Corazón',
  host_kit_color: 'Oscuro',
  guest_kit_color: 'Claro',
  substitutions: null,
  field_cost_split: 'HALF',
  referee_cost_split: 'HALF',
  cancellation_notice_hours: 24,
  foul_caller_note: null,
  extra_rules: null,
};

export const version = (n: number, signedBy: ContractVersion['signed_by'] = []): ContractVersion => ({
  version: n,
  terms,
  proposed_by_side: n === 1 ? null : 'GUEST',
  note: null,
  created_at: '2026-11-23T15:00:00+00:00',
  signed_by: signedBy,
});

export function contract(overrides: Partial<Contract> = {}): Contract {
  const current = version(1);
  return {
    id: 7,
    request_id: 3,
    host: team(1, 'Águilas'),
    guest: team(2, 'Bravos'),
    status: 'NEGOTIATING',
    my_side: 'HOST',
    is_admin: true,
    is_staff: true,
    current,
    signed: null,
    versions: [current],
    cancel_reason: null,
    result: null,
    booking: null,
    ready_to_play: false,
    referee: null,
    league_id: null,
    ...overrides,
  };
}

export const idleAction = (): Action => ({ busy: false, message: null, run: jest.fn(async () => undefined) });

export function contractController(data: Contract): ContractController {
  return {
    state: { kind: 'success', data },
    handleReload: jest.fn(),
    action: idleAction(),
    handleSign: jest.fn(async () => undefined),
    handleRejectAmendment: jest.fn(async () => undefined),
    handleCancel: jest.fn(async () => undefined),
    handleReport: jest.fn(async () => undefined),
    handleCancelBooking: jest.fn(async () => undefined),
  };
}
