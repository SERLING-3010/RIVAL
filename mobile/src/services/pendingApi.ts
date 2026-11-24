import type { PendingItem } from '../domain/pendingModels';
import { request } from './httpClient';

export const pendingApi = {
  mine: (token: string) => request<PendingItem[]>('GET', '/api/v1/me/pending', { token }),
};
