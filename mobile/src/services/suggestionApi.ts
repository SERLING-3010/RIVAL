import type { Suggestion } from '../domain/suggestionModels';
import { request } from './httpClient';

export const suggestionApi = {
  rivals: (token: string, teamId: number) =>
    request<Suggestion[]>('GET', `/api/v1/teams/${teamId}/suggestions`, { token }),
};
