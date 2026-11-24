import type {
  MatchRequest,
  MatchRequestPayload,
  Offer,
  OfferPayload,
  SearchScope,
} from '../domain/matchModels';
import { request } from './httpClient';

type Status = { id: number; status: string };

export const matchApi = {
  create: (token: string, teamId: number, payload: MatchRequestPayload) =>
    request<MatchRequest>('POST', `/api/v1/teams/${teamId}/match-requests`, { token, body: payload }),

  mine: (token: string, teamId: number) =>
    request<MatchRequest[]>('GET', `/api/v1/teams/${teamId}/match-requests`, { token }),

  feed: (token: string, teamId: number, scope: SearchScope, radiusKm: number) =>
    request<MatchRequest[]>('GET', `/api/v1/teams/${teamId}/match-feed`, {
      token,
      query: { scope, radius_km: String(radiusKm) },
    }),

  cancel: (token: string, requestId: number) =>
    request<Status>('POST', `/api/v1/match-requests/${requestId}/cancel`, { token }),

  offer: (token: string, teamId: number, requestId: number, payload: OfferPayload) =>
    request<Status & { version: number }>(
      'POST',
      `/api/v1/teams/${teamId}/match-requests/${requestId}/offers`,
      {
        token,
        body: payload,
      },
    ),

  offers: (token: string, requestId: number) =>
    request<Offer[]>('GET', `/api/v1/match-requests/${requestId}/offers`, { token }),

  decide: (token: string, offerId: number, action: 'accept' | 'reject' | 'withdraw') =>
    request<Status>('POST', `/api/v1/offers/${offerId}/${action}`, { token }),
};
