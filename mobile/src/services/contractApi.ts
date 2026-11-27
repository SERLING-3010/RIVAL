import type { ActivityItem } from '../domain/activityLabels';
import type { Contract, ContractSummary, ContractTerms } from '../domain/contractModels';
import { request } from './httpClient';

export const contractApi = {
  forTeam: (token: string, teamId: number) =>
    request<ContractSummary[]>('GET', `/api/v1/teams/${teamId}/contracts`, { token }),

  get: (token: string, contractId: number) =>
    request<Contract>('GET', `/api/v1/contracts/${contractId}`, { token }),

  propose: (
    token: string,
    contractId: number,
    baseVersion: number,
    terms: ContractTerms,
    note: string | null,
  ) =>
    request<Contract>('POST', `/api/v1/contracts/${contractId}/proposals`, {
      token,
      body: { base_version: baseVersion, terms, note },
    }),

  sign: (token: string, contractId: number, version: number) =>
    request<Contract>('POST', `/api/v1/contracts/${contractId}/sign`, { token, body: { version } }),

  rejectAmendment: (token: string, contractId: number, version: number) =>
    request<Contract>('POST', `/api/v1/contracts/${contractId}/reject-amendment`, {
      token,
      body: { version },
    }),

  cancel: (token: string, contractId: number, reason: string) =>
    request<Contract>('POST', `/api/v1/contracts/${contractId}/cancel`, { token, body: { reason } }),

  reportResult: (token: string, contractId: number, hostScore: number, guestScore: number) =>
    request<Contract>('POST', `/api/v1/contracts/${contractId}/result`, {
      token,
      body: { host_score: hostScore, guest_score: guestScore },
    }),

  activity: (token: string, scope: 'contracts' | 'teams', id: number) =>
    request<ActivityItem[]>('GET', `/api/v1/${scope}/${id}/activity`, { token }),
};
