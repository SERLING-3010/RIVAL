import type { Cup } from '../domain/cupModels';
import { request } from './httpClient';

export const cupApi = {
  get: (token: string, leagueId: number) => request<Cup>('GET', `/api/v1/leagues/${leagueId}/cup`, { token }),

  create: (token: string, leagueId: number, firstKickoff: string, daysBetween: number) =>
    request<Cup>('POST', `/api/v1/leagues/${leagueId}/cup`, {
      token,
      body: { first_kickoff: firstKickoff, days_between: daysBetween },
    }),

  tiebreak: (token: string, cupMatchId: number, winnerTeamId: number) =>
    request<{ id: number }>('POST', `/api/v1/cup-matches/${cupMatchId}/tiebreak`, {
      token,
      body: { winner_team_id: winnerTeamId },
    }),
};
