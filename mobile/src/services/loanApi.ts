import type { Loan } from '../domain/loanModels';
import { request } from './httpClient';

export type LoanDecision = 'owner-accept' | 'owner-reject' | 'player-accept' | 'player-reject' | 'cancel';

export const loanApi = {
  forContract: (token: string, contractId: number) =>
    request<Loan[]>('GET', `/api/v1/contracts/${contractId}/loans`, { token }),

  request: (token: string, contractId: number, playerId: number, fromTeamId: number) =>
    request<Loan[]>('POST', `/api/v1/contracts/${contractId}/loans`, {
      token,
      body: { player_id: playerId, from_team_id: fromTeamId },
    }),

  mine: (token: string) => request<Loan[]>('GET', '/api/v1/me/loans', { token }),

  decide: (token: string, loanId: number, decision: LoanDecision) =>
    request<{ id: number; status: string }>('POST', `/api/v1/loans/${loanId}/${decision}`, { token }),

  setWindow: (token: string, leagueId: number, startsAt: string | null, endsAt: string | null) =>
    request<{ league_id: number }>('POST', `/api/v1/leagues/${leagueId}/transfer-window`, {
      token,
      body: { starts_at: startsAt, ends_at: endsAt },
    }),
};
