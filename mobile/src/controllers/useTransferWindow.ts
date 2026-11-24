// Ventana de traspasos de una liga: la fija o la quita el organizador (Sprint 13).

import { useCallback } from 'react';

import { loanApi } from '../services/loanApi';
import type { Action } from './useAction';
import { useAction } from './useAction';

export interface TransferWindowController {
  action: Action;
  handleSave: (startsAt: string, endsAt: string) => Promise<void>;
  handleClear: () => Promise<void>;
}

export function useTransferWindow(
  token: string,
  leagueId: number,
  onDone: () => void,
): TransferWindowController {
  const action = useAction();
  const handleSave = useCallback(
    (startsAt: string, endsAt: string) =>
      action.run(
        () => loanApi.setWindow(token, leagueId, startsAt, endsAt),
        'Ventana de traspasos guardada.',
        onDone,
      ),
    [action, leagueId, onDone, token],
  );
  const handleClear = useCallback(
    () =>
      action.run(
        () => loanApi.setWindow(token, leagueId, null, null),
        'Ventana quitada: traspasos abiertos.',
        onDone,
      ),
    [action, leagueId, onDone, token],
  );
  return { action, handleSave, handleClear };
}
