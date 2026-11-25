import type { Tactic } from '../domain/tacticsModels';
import { request } from './httpClient';

export interface TacticBody {
  formation: string | null;
  starters: { user_id: number; position: string }[];
  subs: number[];
}

export const tacticsApi = {
  get: (token: string, contractId: number) =>
    request<Tactic>('GET', `/api/v1/contracts/${contractId}/tactics`, { token }),

  save: (token: string, contractId: number, body: TacticBody) =>
    request<Tactic>('POST', `/api/v1/contracts/${contractId}/tactics`, { token, body }),
};
