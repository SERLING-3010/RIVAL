import type { Squad } from '../domain/squadModels';
import { request } from './httpClient';

export const squadApi = {
  get: (token: string, teamId: number) => request<Squad>('GET', `/api/v1/teams/${teamId}/squad`, { token }),

  // Sprint 23: el administrador elige el diseño del cuadro de la media y arma el escudo.
  chooseDesign: (token: string, teamId: number, choice: string | null) =>
    request<Squad>('POST', `/api/v1/teams/${teamId}/card-choice`, { token, body: { choice } }),

  setCrest: (token: string, teamId: number, crest: string | null) =>
    request<Squad>('POST', `/api/v1/teams/${teamId}/crest`, { token, body: { crest } }),
};
