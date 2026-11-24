// Acción con cerrojo contra doble toque, estado ocupado y mensaje de resultado.

import { useCallback, useState } from 'react';

import { toAppError } from '../domain/appError';
import { useSubmitLock } from './useSubmitLock';

export interface Action {
  busy: boolean;
  message: string | null;
  run: (action: () => Promise<unknown>, success: string, after?: () => void) => Promise<void>;
}

export function useAction(): Action {
  const lock = useSubmitLock();
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const run = useCallback(
    async (action: () => Promise<unknown>, success: string, after?: () => void) => {
      await lock(async () => {
        setBusy(true);
        setMessage(null);
        try {
          await action();
          setMessage(success);
          after?.();
        } catch (error) {
          setMessage(toAppError(error).message);
        } finally {
          setBusy(false);
        }
      });
    },
    [lock],
  );
  return { busy, message, run };
}
