import { request } from './httpClient';

// Registrar o quitar el teléfono para avisos (Sprint 24). Solo viaja el identificador de Expo.
export const pushApi = {
  register: (token: string, deviceToken: string) =>
    request<null>('POST', '/api/v1/me/push-devices', { token, body: { token: deviceToken } }),

  remove: (token: string, deviceToken: string) =>
    request<null>('POST', '/api/v1/me/push-devices/remove', { token, body: { token: deviceToken } }),
};
