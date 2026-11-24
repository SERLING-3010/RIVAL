import { useCallback, useEffect, useState } from 'react';

import { errorToViewState } from '../domain/appError';
import type { MyTeam } from '../domain/models';
import type { ViewState } from '../domain/viewState';
import { successOrEmpty } from '../domain/viewState';
import { teamApi } from '../services/teamApi';

export function useMyTeams(token: string): { state: ViewState<MyTeam[]>; handleRefresh: () => void } {
  const [state, setState] = useState<ViewState<MyTeam[]>>({ kind: 'loading' });
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let active = true;
    setState({ kind: 'loading' });
    teamApi
      .mine(token)
      .then((teams) => {
        if (active) {
          setState(successOrEmpty(teams, teams.length === 0, 'Todavía no tienes equipo.'));
        }
      })
      .catch((error: unknown) => {
        if (active) setState(errorToViewState<MyTeam[]>(error));
      });
    return () => {
      active = false;
    };
  }, [token, attempt]);

  const handleRefresh = useCallback(() => setAttempt((n) => n + 1), []);
  return { state, handleRefresh };
}
