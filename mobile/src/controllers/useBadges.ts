// Insignias de un jugador o de un equipo.

import type { Badge, BadgeOwner } from '../domain/badgeModels';
import { badgeApi } from '../services/badgeApi';
import type { Loader } from './useLoader';
import { useLoader } from './useLoader';

export function useBadges(token: string, owner: BadgeOwner, id: number): Loader<Badge[]> {
  return useLoader(
    () => badgeApi.list(token, owner, id),
    () => false,
    '',
    `badges|${owner}|${id}`,
  );
}
