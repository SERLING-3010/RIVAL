import type { Fixture, RefereeMatch, Standing } from '../domain/seasonModels';
import { request } from './httpClient';

export const seasonApi = {
  calendar: (token: string, leagueId: number) =>
    request<Fixture[]>('GET', `/api/v1/leagues/${leagueId}/calendar`, { token }),

  table: (token: string, leagueId: number) =>
    request<Standing[]>('GET', `/api/v1/leagues/${leagueId}/table`, { token }),

  generate: (token: string, leagueId: number, firstKickoff: string, daysBetween: number) =>
    request<Fixture[]>('POST', `/api/v1/leagues/${leagueId}/fixtures`, {
      token,
      body: { first_kickoff: firstKickoff, days_between: daysBetween },
    }),

  assignReferee: (token: string, contractId: number, refereeId: number) =>
    request<{ assignment_id: number }>('POST', `/api/v1/contracts/${contractId}/referee`, {
      token,
      body: { referee_id: refereeId },
    }),

  myMatches: (token: string) => request<RefereeMatch[]>('GET', '/api/v1/me/referee-matches', { token }),

  respond: (token: string, assignmentId: number, accept: boolean) =>
    request<RefereeMatch[]>(
      'POST',
      `/api/v1/referee-assignments/${assignmentId}/${accept ? 'accept' : 'decline'}`,
      { token },
    ),

  report: (token: string, contractId: number, hostScore: number, guestScore: number) =>
    request<RefereeMatch[]>('POST', `/api/v1/contracts/${contractId}/referee-result`, {
      token,
      body: { host_score: hostScore, guest_score: guestScore },
    }),
};
