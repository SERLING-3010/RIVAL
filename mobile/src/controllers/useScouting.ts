// Buscar rivales y agentes libres, e invitar. Solo barrio, ciudad y rangos de distancia.

import { useCallback, useState } from 'react';

import type { FreeAgent, Rival, SearchScope } from '../domain/matchModels';
import type { TeamSummary } from '../domain/models';
import { scoutingApi } from '../services/scoutingApi';
import type { Action } from './useAction';
import { useAction } from './useAction';
import type { PagedLoader } from './usePagedLoader';
import { usePagedLoader } from './usePagedLoader';

export interface RivalSearchController extends PagedLoader<Rival> {
  scope: SearchScope;
  radiusKm: number;
  handleScope: (scope: SearchScope) => void;
  handleRadius: (km: number) => void;
}

export function useRivalSearch(token: string, teamId: number): RivalSearchController {
  const [scope, setScope] = useState<SearchScope>('NEARBY');
  const [radiusKm, setRadiusKm] = useState(5);
  const loader = usePagedLoader(
    (page) => scoutingApi.rivals(token, teamId, scope, radiusKm, page),
    'No hay equipos de tu deporte y modalidad en ese alcance. Prueba con "Mi ciudad".',
    `${teamId}|${scope}|${radiusKm}`,
  );
  return { ...loader, scope, radiusKm, handleScope: setScope, handleRadius: setRadiusKm };
}

export interface FreeAgentSearchController extends PagedLoader<FreeAgent> {
  onlyMyNeighborhood: boolean;
  invited: Record<number, string>;
  action: Action;
  handleOnlyNeighborhood: (value: boolean) => void;
  handleInvite: (userId: number) => Promise<void>;
}

export function useFreeAgentSearch(token: string, team: TeamSummary): FreeAgentSearchController {
  const [onlyMyNeighborhood, setOnlyMyNeighborhood] = useState(false);
  const [invited, setInvited] = useState<Record<number, string>>({});
  const action = useAction();
  const loader = usePagedLoader(
    (page) =>
      scoutingApi.freeAgents(
        token,
        team.sport_code,
        team.city,
        onlyMyNeighborhood ? team.neighborhood : undefined,
        page,
      ),
    'No hay agentes libres de este deporte por ahora.',
    `${team.id}|${onlyMyNeighborhood}`,
  );
  const handleInvite = useCallback(
    (userId: number) =>
      action.run(
        () => scoutingApi.invite(token, team.id, userId),
        'Invitación enviada. La persona debe aceptarla.',
        () => setInvited((s) => ({ ...s, [userId]: 'Invitado' })),
      ),
    [action, team.id, token],
  );
  return {
    ...loader,
    onlyMyNeighborhood,
    invited,
    action,
    handleOnlyNeighborhood: setOnlyMyNeighborhood,
    handleInvite,
  };
}
