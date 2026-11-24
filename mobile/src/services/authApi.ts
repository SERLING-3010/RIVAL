import type { RegisterPayload, SessionResponse, Sport, User } from '../domain/models';
import { request } from './httpClient';

export const authApi = {
  register: (payload: RegisterPayload) =>
    request<SessionResponse>('POST', '/api/v1/auth/register', { body: payload }),

  login: (email: string, password: string) =>
    request<SessionResponse>('POST', '/api/v1/auth/login', { body: { email, password } }),

  logout: (token: string) => request<void>('POST', '/api/v1/auth/logout', { token }),

  me: (token: string) => request<User>('GET', '/api/v1/me', { token }),

  sports: async () => (await request<{ sports: Sport[] }>('GET', '/api/v1/catalog/sports')).sports,
};
