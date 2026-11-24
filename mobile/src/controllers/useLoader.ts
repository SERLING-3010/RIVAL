// Carga genérica con los 7 estados: evita repetir el mismo efecto en cada controlador.

import { useCallback, useEffect, useRef, useState } from 'react';

import { errorToViewState } from '../domain/appError';
import type { ViewState } from '../domain/viewState';
import { successOrEmpty } from '../domain/viewState';

export interface Loader<T> {
  state: ViewState<T>;
  handleReload: () => void;
}

export function useLoader<T>(
  load: () => Promise<T>,
  isEmpty: (data: T) => boolean,
  emptyMessage: string,
  key: string,
): Loader<T> {
  const [state, setState] = useState<ViewState<T>>({ kind: 'loading' });
  const [attempt, setAttempt] = useState(0);
  const loadRef = useRef(load);
  loadRef.current = load;

  useEffect(() => {
    let active = true;
    setState({ kind: 'loading' });
    loadRef
      .current()
      .then((data) => {
        if (active) setState(successOrEmpty(data, isEmpty(data), emptyMessage));
      })
      .catch((error: unknown) => {
        if (active) setState(errorToViewState<T>(error));
      });
    return () => {
      active = false;
    };
    // `key` resume todo lo que cambia la consulta; `isEmpty` y el mensaje son estables.
  }, [key, attempt]);

  return { state, handleReload: useCallback(() => setAttempt((n) => n + 1), []) };
}
