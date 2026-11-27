import type { Badge, BadgeOwner } from '../domain/badgeModels';
import { request } from './httpClient';

export const badgeApi = {
  list: (token: string, owner: BadgeOwner, id: number) =>
    request<Badge[]>('GET', `/api/v1/${owner === 'player' ? 'players' : 'teams'}/${id}/badges`, { token }),
};
