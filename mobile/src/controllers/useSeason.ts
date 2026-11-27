// Temporada de la liga (calendario y tabla) y partidos del árbitro.

import { useCallback } from 'react';

import { parseLocalDateTime } from '../domain/dateTime';
import type { RefereeMatch, Season } from '../domain/seasonModels';
import { seasonApi } from '../services/seasonApi';
import type { Action } from './useAction';
import { useAction } from './useAction';
import type { Loader } from './useLoader';
import { useLoader } from './useLoader';

export interface SeasonController extends Loader<Season> {
  action: Action;
  /** Devuelve un error de validación local, o null si se envió. */
  handleGenerate: (firstText: string, daysText: string) => Promise<string | null>;
  handleAssign: (contractId: number, refereeId: number) => Promise<void>;
}

export function useSeason(token: string, leagueId: number): SeasonController {
  const action = useAction();
  const loader = useLoader(
    async () => {
      const [calendar, table] = await Promise.all([
        seasonApi.calendar(token, leagueId),
        seasonApi.table(token, leagueId),
      ]);
      return { calendar, table };
    },
    () => false,
    '',
    `season|${leagueId}`,
  );
  const { handleReload } = loader;
  const handleGenerate = useCallback(
    async (firstText: string, daysText: string) => {
      const first = parseLocalDateTime(firstText);
      const days = /^\d{1,2}$/.test(daysText.trim()) ? Number(daysText) : 0;
      if (!first) return 'Escribe la primera fecha como dd/mm/aaaa hh:mm.';
      if (days < 1 || days > 14) return 'Entre fechas deben pasar de 1 a 14 días.';
      await action.run(
        () => seasonApi.generate(token, leagueId, first, days),
        'Calendario creado.',
        handleReload,
      );
      return null;
    },
    [action, handleReload, leagueId, token],
  );
  const handleAssign = useCallback(
    (contractId: number, refereeId: number) =>
      action.run(
        () => seasonApi.assignReferee(token, contractId, refereeId),
        'Árbitro asignado. Debe aceptar el partido.',
        handleReload,
      ),
    [action, handleReload, token],
  );
  return { ...loader, action, handleGenerate, handleAssign };
}

export interface RefereeMatchesController extends Loader<RefereeMatch[]> {
  action: Action;
  handleRespond: (assignmentId: number, accept: boolean) => Promise<void>;
  handleReport: (contractId: number, hostScore: number, guestScore: number) => Promise<void>;
}

export function useRefereeMatches(token: string): RefereeMatchesController {
  const action = useAction();
  const loader = useLoader(
    () => seasonApi.myMatches(token),
    (items) => items.length === 0,
    'No tienes partidos asignados. El personal de tus ligas te los asigna.',
    'referee-matches',
  );
  const { handleReload } = loader;
  const handleRespond = useCallback(
    (assignmentId: number, accept: boolean) =>
      action.run(
        () => seasonApi.respond(token, assignmentId, accept),
        accept ? 'Partido aceptado.' : 'Partido rechazado.',
        handleReload,
      ),
    [action, handleReload, token],
  );
  const handleReport = useCallback(
    (contractId: number, hostScore: number, guestScore: number) =>
      action.run(
        () => seasonApi.report(token, contractId, hostScore, guestScore),
        'Resultado fijado. Ya cuenta en la tabla.',
        handleReload,
      ),
    [action, handleReload, token],
  );
  return { ...loader, action, handleRespond, handleReport };
}
