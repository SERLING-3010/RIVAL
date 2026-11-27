import type {
  FreeAgentPage,
  FreeAgentProfile,
  Invitation,
  RivalPage,
  SearchScope,
} from '../domain/matchModels';
import { request } from './httpClient';

/** default: por cercanía o nombre; level: nivel parecido al de mi equipo primero (Sprint 11). */
export type RivalOrder = 'default' | 'level';

export const scoutingApi = {
  rivals: (
    token: string,
    teamId: number,
    scope: SearchScope,
    radiusKm: number,
    page: number,
    order: RivalOrder = 'default',
  ) =>
    request<RivalPage>('GET', `/api/v1/teams/${teamId}/rivals`, {
      token,
      query: { scope, radius_km: String(radiusKm), page: String(page), order },
    }),

  myFreeAgent: (token: string) => request<FreeAgentProfile[]>('GET', '/api/v1/me/free-agent', { token }),

  setFreeAgent: (token: string, profile: FreeAgentProfile) =>
    request<FreeAgentProfile>('POST', '/api/v1/me/free-agent', { token, body: profile }),

  freeAgents: (token: string, sport: string, city: string, neighborhood: string | undefined, page: number) =>
    request<FreeAgentPage>('GET', '/api/v1/free-agents', {
      token,
      query: { sport, city, neighborhood, page: String(page) },
    }),

  invite: (token: string, teamId: number, userId: number) =>
    request<{ id: number; status: string }>('POST', `/api/v1/teams/${teamId}/invitations`, {
      token,
      body: { user_id: userId },
    }),

  myInvitations: (token: string) => request<Invitation[]>('GET', '/api/v1/me/invitations', { token }),

  respondInvitation: (token: string, invitationId: number, accept: boolean) =>
    request<{ id: number; status: string }>(
      'POST',
      `/api/v1/invitations/${invitationId}/${accept ? 'accept' : 'reject'}`,
      { token },
    ),
};
