// Ligas: mis ligas y búsqueda, y detalle de una liga con sus acciones.

import { useCallback, useState } from 'react';

import type { EntryKind, LeagueDetail, LeaguePage, MyLeague } from '../domain/leagueModels';
import type { User } from '../domain/models';
import { leagueApi } from '../services/leagueApi';
import type { Action } from './useAction';
import { useAction } from './useAction';
import type { Loader } from './useLoader';
import { useLoader } from './useLoader';

export interface LeagueHomeController {
  mine: Loader<MyLeague[]>;
  results: Loader<LeaguePage>;
  query: string;
  handleQuery: (text: string) => void;
  handleSearch: () => void;
}

export function useLeagueHome(token: string, user: User): LeagueHomeController {
  const [query, setQuery] = useState('');
  const [submitted, setSubmitted] = useState('');
  const mine = useLoader(
    () => leagueApi.mine(token),
    (items) => items.length === 0,
    'Aún no haces parte de ninguna liga.',
    'my-leagues',
  );
  const results = useLoader(
    () => leagueApi.search(token, { city: user.city, q: submitted || undefined }),
    (page) => page.items.length === 0,
    `No encontramos ligas en ${user.city} con ese nombre. Puedes crear una.`,
    `leagues|${user.city}|${submitted}`,
  );
  const handleSearch = useCallback(() => setSubmitted(query.trim()), [query]);
  return { mine, results, query, handleQuery: setQuery, handleSearch };
}

export interface LeagueController extends Loader<LeagueDetail> {
  action: Action;
  handleRequestTeam: (teamId: number) => Promise<void>;
  handleJoinAsReferee: () => Promise<void>;
  handleCloseSeason: () => Promise<void>; // Sprint 23
  handleDecide: (
    kind: EntryKind,
    entryId: number,
    decision: 'approve' | 'reject' | 'withdraw',
  ) => Promise<void>;
}

const DECISION_MESSAGE = {
  approve: 'Solicitud aprobada.',
  reject: 'Solicitud rechazada.',
  withdraw: 'Listo, se retiró la solicitud.',
} as const;

export function useLeague(token: string, leagueId: number): LeagueController {
  const action = useAction();
  const loader = useLoader(
    () => leagueApi.get(token, leagueId),
    () => false,
    '',
    `league|${leagueId}`,
  );
  const { handleReload } = loader;
  const handleRequestTeam = useCallback(
    (teamId: number) =>
      action.run(
        () => leagueApi.requestTeam(token, leagueId, teamId),
        'Solicitud enviada. El organizador debe aprobarla.',
        handleReload,
      ),
    [action, handleReload, leagueId, token],
  );
  const handleJoinAsReferee = useCallback(
    () =>
      action.run(
        () => leagueApi.requestReferee(token, leagueId),
        'Solicitud enviada al cuerpo arbitral.',
        handleReload,
      ),
    [action, handleReload, leagueId, token],
  );
  const handleDecide = useCallback(
    (kind: EntryKind, entryId: number, decision: 'approve' | 'reject' | 'withdraw') =>
      action.run(
        () => leagueApi.decide(token, kind, entryId, decision),
        DECISION_MESSAGE[decision],
        handleReload,
      ),
    [action, handleReload, token],
  );
  const handleCloseSeason = useCallback(
    () =>
      action.run(
        () => leagueApi.closeSeason(token, leagueId),
        'Temporada cerrada. ¡Ya hay campeón!',
        handleReload,
      ),
    [action, handleReload, leagueId, token],
  );
  return { ...loader, action, handleRequestTeam, handleJoinAsReferee, handleDecide, handleCloseSeason };
}
