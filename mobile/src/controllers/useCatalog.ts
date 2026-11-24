import { useCallback, useEffect, useState } from 'react';

import { errorToViewState } from '../domain/appError';
import type { Sport } from '../domain/models';
import type { ViewState } from '../domain/viewState';
import { successOrEmpty } from '../domain/viewState';
import { authApi } from '../services/authApi';

export function useCatalog(): { state: ViewState<Sport[]>; handleRetry: () => void } {
  const [state, setState] = useState<ViewState<Sport[]>>({ kind: 'loading' });
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let active = true;
    setState({ kind: 'loading' });
    authApi
      .sports()
      .then((sports) => {
        if (active) setState(successOrEmpty(sports, sports.length === 0, 'No hay deportes configurados.'));
      })
      .catch((error: unknown) => {
        if (active) setState(errorToViewState<Sport[]>(error));
      });
    return () => {
      active = false;
    };
  }, [attempt]);

  const handleRetry = useCallback(() => setAttempt((n) => n + 1), []);
  return { state, handleRetry };
}

export function sportName(sports: Sport[], code: string): string {
  return sports.find((s) => s.code === code)?.name ?? code;
}
