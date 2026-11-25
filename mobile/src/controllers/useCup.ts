// Copa de la liga: ver el cuadro, armarla (organizador) y definir empates por penales.

import { useCallback } from 'react';

import type { Cup } from '../domain/cupModels';
import { parseSchedule } from '../domain/cupModels';
import { cupApi } from '../services/cupApi';
import type { Action } from './useAction';
import { useAction } from './useAction';
import type { Loader } from './useLoader';
import { useLoader } from './useLoader';

export interface CupController extends Loader<Cup> {
  action: Action;
  /** Devuelve el error del formulario, o null si se envió. */
  handleCreate: (firstText: string, daysText: string) => Promise<string | null>;
  handleTiebreak: (cupMatchId: number, winnerTeamId: number) => Promise<void>;
}

export function useCup(token: string, leagueId: number): CupController {
  const action = useAction();
  const loader = useLoader(
    () => cupApi.get(token, leagueId),
    () => false,
    '',
    `cup|${leagueId}`,
  );
  const { handleReload } = loader;
  const handleCreate = useCallback(
    async (firstText: string, daysText: string) => {
      const schedule = parseSchedule(firstText, daysText);
      if (!schedule.ok) return schedule.error;
      await action.run(
        () => cupApi.create(token, leagueId, schedule.first, schedule.days),
        'Copa armada. Los primeros cruces ya tienen su partido para firmar.',
        handleReload,
      );
      return null;
    },
    [action, handleReload, leagueId, token],
  );
  const handleTiebreak = useCallback(
    (cupMatchId: number, winnerTeamId: number) =>
      action.run(
        () => cupApi.tiebreak(token, cupMatchId, winnerTeamId),
        'Ganador por penales guardado.',
        handleReload,
      ),
    [action, handleReload, token],
  );
  return { ...loader, action, handleCreate, handleTiebreak };
}
