import type { MyCallUp, Rateable, TeamCallUp } from '../domain/matchdayModels';
import { request } from './httpClient';

export const matchdayApi = {
  callup: (token: string, contractId: number) =>
    request<TeamCallUp>('GET', `/api/v1/contracts/${contractId}/callup`, { token }),

  send: (token: string, contractId: number, userIds: number[]) =>
    request<TeamCallUp>('POST', `/api/v1/contracts/${contractId}/callup`, {
      token,
      body: { user_ids: userIds },
    }),

  respond: (token: string, contractId: number, going: boolean) =>
    request<TeamCallUp>('POST', `/api/v1/contracts/${contractId}/callup/respond`, { token, body: { going } }),

  mine: (token: string) => request<MyCallUp[]>('GET', '/api/v1/me/callups', { token }),

  pendingRatings: (token: string, contractId: number) =>
    request<Rateable[]>('GET', `/api/v1/contracts/${contractId}/ratings/pending`, { token }),

  rate: (token: string, contractId: number, ratedId: number, score: number) =>
    request<Rateable[]>('POST', `/api/v1/contracts/${contractId}/ratings`, {
      token,
      body: { rated_id: ratedId, score },
    }),
};
