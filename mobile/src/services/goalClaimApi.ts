import type { GoalClaim, GoalClaimStatus } from '../domain/goalKinds';
import { request } from './httpClient';

// Goles con tipo del partido (Sprint 23) y la decisión del rival.
export const goalClaimApi = {
  list: (token: string, contractId: number) =>
    request<GoalClaim[]>('GET', `/api/v1/contracts/${contractId}/goal-claims`, { token }),

  decide: (token: string, claimId: number, accept: boolean) =>
    request<{ status: GoalClaimStatus }>('POST', `/api/v1/goal-claims/${claimId}/decision`, {
      token,
      body: { accept },
    }),
};
