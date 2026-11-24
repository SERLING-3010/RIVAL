// Cerrojo síncrono contra el doble toque: el estado de React llega un render tarde,
// una referencia no. Dos toques en el mismo instante ejecutan la acción una sola vez.

import { useCallback, useRef } from 'react';

export function useSubmitLock(): <T>(action: () => Promise<T>) => Promise<T | undefined> {
  const locked = useRef(false);
  return useCallback(async <T>(action: () => Promise<T>): Promise<T | undefined> => {
    if (locked.current) {
      return undefined;
    }
    locked.current = true;
    try {
      return await action();
    } finally {
      locked.current = false;
    }
  }, []);
}
