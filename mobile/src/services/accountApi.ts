import type { User } from '../domain/models';
import { request } from './httpClient';

// Mis datos (Sprint 27, Ley 1581): aceptar términos, descargar mis datos y eliminar la cuenta.
export const accountApi = {
  acceptTerms: (token: string, version: string) =>
    request<User>('POST', '/api/v1/me/accept-terms', { token, body: { version } }),

  exportData: (token: string) => request<Record<string, unknown>>('GET', '/api/v1/me/data-export', { token }),

  deleteAccount: (token: string, password: string) =>
    request<null>('POST', '/api/v1/me/delete-account', { token, body: { password } }),
};
