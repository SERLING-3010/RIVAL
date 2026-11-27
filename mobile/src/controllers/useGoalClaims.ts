// Goles con tipo del partido (Sprint 23): la lista y la decisión del DT o capitán rival.

import { useCallback } from 'react';

import type { GoalClaim } from '../domain/goalKinds';
import { goalClaimApi } from '../services/goalClaimApi';
import type { Action } from './useAction';
import { useAction } from './useAction';
import type { Loader } from './useLoader';
import { useLoader } from './useLoader';

export interface GoalClaimsController extends Loader<GoalClaim[]> {
  action: Action;
  handleDecide: (claimId: number, accept: boolean) => Promise<void>;
}

export function useGoalClaims(token: string, contractId: number): GoalClaimsController {
  const loader = useLoader(
    () => goalClaimApi.list(token, contractId),
    (claims) => claims.length === 0,
    'Sin goles con tipo en este partido.',
    `goal-claims-${contractId}`,
  );
  const action = useAction();
  const { handleReload } = loader;
  const handleDecide = useCallback(
    async (claimId: number, accept: boolean) => {
      await action.run(
        () => goalClaimApi.decide(token, claimId, accept),
        accept ? 'Gol confirmado: cuenta para sus hazañas.' : 'Gol rechazado: queda como gol normal.',
        handleReload,
      );
    },
    [action, handleReload, token],
  );
  return { ...loader, action, handleDecide };
}
