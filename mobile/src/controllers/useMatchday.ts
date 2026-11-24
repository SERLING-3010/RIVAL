// Día del partido: convocatoria del equipo, mis convocatorias y valoraciones de compañeros.

import { useCallback } from 'react';

import type { MyCallUp, Rateable, TeamCallUp } from '../domain/matchdayModels';
import { matchdayApi } from '../services/matchdayApi';
import type { Action } from './useAction';
import { useAction } from './useAction';
import type { Loader } from './useLoader';
import { useLoader } from './useLoader';

export interface CallUpController extends Loader<TeamCallUp> {
  action: Action;
  handleSend: (userIds: number[]) => Promise<void>;
  handleRespond: (going: boolean) => Promise<void>;
}

export function useCallUp(token: string, contractId: number): CallUpController {
  const action = useAction();
  const loader = useLoader(
    () => matchdayApi.callup(token, contractId),
    () => false,
    '',
    `callup|${contractId}`,
  );
  const { handleReload } = loader;
  const handleSend = useCallback(
    (userIds: number[]) =>
      action.run(() => matchdayApi.send(token, contractId, userIds), 'Convocatoria enviada.', handleReload),
    [action, contractId, handleReload, token],
  );
  const handleRespond = useCallback(
    (going: boolean) =>
      action.run(
        () => matchdayApi.respond(token, contractId, going),
        going ? '¡Listo! Tu equipo sabe que vas.' : 'Avisaste que no vas.',
        handleReload,
      ),
    [action, contractId, handleReload, token],
  );
  return { ...loader, action, handleSend, handleRespond };
}

export function useMyCallUps(token: string): Loader<MyCallUp[]> {
  return useLoader(
    () => matchdayApi.mine(token),
    (items) => items.length === 0,
    'No tienes convocatorias para partidos próximos.',
    'my-callups',
  );
}

export interface RatingsController extends Loader<Rateable[]> {
  action: Action;
  handleRate: (ratedId: number, score: number) => Promise<void>;
}

export function useRatings(token: string, contractId: number): RatingsController {
  const action = useAction();
  const loader = useLoader(
    () => matchdayApi.pendingRatings(token, contractId),
    (items) => items.length === 0,
    'No te quedan compañeros por valorar en este partido.',
    `ratings|${contractId}`,
  );
  const { handleReload } = loader;
  const handleRate = useCallback(
    (ratedId: number, score: number) =>
      action.run(
        () => matchdayApi.rate(token, contractId, ratedId, score),
        'Valoración guardada.',
        handleReload,
      ),
    [action, contractId, handleReload, token],
  );
  return { ...loader, action, handleRate };
}
