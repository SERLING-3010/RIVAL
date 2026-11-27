// Central de actividad de un equipo o de un partido.

import type { ActivityItem } from '../domain/activityLabels';
import { contractApi } from '../services/contractApi';
import type { Loader } from './useLoader';
import { useLoader } from './useLoader';

export type ActivityScope = 'contracts' | 'teams';

export function useActivity(token: string, scope: ActivityScope, id: number): Loader<ActivityItem[]> {
  return useLoader(
    () => contractApi.activity(token, scope, id),
    (items) => items.length === 0,
    'Todavía no hay actividad registrada.',
    `activity|${scope}|${id}`,
  );
}
