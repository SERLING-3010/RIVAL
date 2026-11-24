import type {
  CreateTeamPayload,
  JoinRequest,
  MyTeam,
  TeamDetail,
  TeamPage,
  TeamRole,
  TeamSearchQuery,
} from '../domain/models';
import { request } from './httpClient';

export const teamApi = {
  search: (token: string, query: TeamSearchQuery) =>
    request<TeamPage>('GET', '/api/v1/teams', {
      token,
      query: { sport: query.sport, city: query.city, q: query.q, page: query.page?.toString() },
    }),

  create: (token: string, payload: CreateTeamPayload) =>
    request<TeamDetail>('POST', '/api/v1/teams', { token, body: payload }),

  detail: (token: string, teamId: number) => request<TeamDetail>('GET', `/api/v1/teams/${teamId}`, { token }),

  mine: (token: string) => request<MyTeam[]>('GET', '/api/v1/me/teams', { token }),

  requestJoin: (token: string, teamId: number, desiredRole: TeamRole) =>
    request<{ id: number; status: string }>('POST', `/api/v1/teams/${teamId}/join-requests`, {
      token,
      body: { desired_role: desiredRole },
    }),

  pendingRequests: (token: string, teamId: number) =>
    request<JoinRequest[]>('GET', `/api/v1/teams/${teamId}/join-requests`, { token }),

  decide: (token: string, requestId: number, approve: boolean) =>
    request<{ id: number; status: string }>(
      'POST',
      `/api/v1/join-requests/${requestId}/${approve ? 'approve' : 'reject'}`,
      { token },
    ),

  setCaptain: (token: string, teamId: number, userId: number) =>
    request<TeamDetail>('POST', `/api/v1/teams/${teamId}/captain`, {
      token,
      body: { user_id: userId },
    }),

  leave: (token: string, teamId: number) => request<void>('POST', `/api/v1/teams/${teamId}/leave`, { token }),
};
