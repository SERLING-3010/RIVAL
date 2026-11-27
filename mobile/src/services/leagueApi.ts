import type {
  CreateLeaguePayload,
  EntryKind,
  LeagueDetail,
  LeaguePage,
  MyLeague,
} from '../domain/leagueModels';
import { request } from './httpClient';

export const leagueApi = {
  create: (token: string, payload: CreateLeaguePayload) =>
    request<LeagueDetail>('POST', '/api/v1/leagues', { token, body: payload }),

  search: (token: string, query: { sport?: string; city?: string; q?: string; page?: number }) =>
    request<LeaguePage>('GET', '/api/v1/leagues', {
      token,
      query: { sport: query.sport, city: query.city, q: query.q, page: String(query.page ?? 1) },
    }),

  mine: (token: string) => request<MyLeague[]>('GET', '/api/v1/me/leagues', { token }),

  get: (token: string, leagueId: number) =>
    request<LeagueDetail>('GET', `/api/v1/leagues/${leagueId}`, { token }),

  requestTeam: (token: string, leagueId: number, teamId: number) =>
    request<LeagueDetail>('POST', `/api/v1/leagues/${leagueId}/team-requests`, {
      token,
      body: { team_id: teamId },
    }),

  requestReferee: (token: string, leagueId: number) =>
    request<LeagueDetail>('POST', `/api/v1/leagues/${leagueId}/referee-requests`, { token }),

  decide: (token: string, kind: EntryKind, entryId: number, decision: 'approve' | 'reject' | 'withdraw') =>
    request<LeagueDetail>('POST', `/api/v1/league-requests/${kind}/${entryId}/${decision}`, { token }),

  closeSeason: (token: string, leagueId: number) =>
    request<LeagueDetail>('POST', `/api/v1/leagues/${leagueId}/close-season`, { token }),
};
