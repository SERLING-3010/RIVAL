// Check-in del partido y ubicación de la cancha: leen el GPS una sola vez y lo mandan al servidor.

import { useCallback } from 'react';

import type { CheckInBoard } from '../domain/checkInModels';
import { checkInApi } from '../services/checkInApi';
import { currentPosition } from '../services/locationService';
import type { Action } from './useAction';
import { useAction } from './useAction';
import type { Loader } from './useLoader';
import { useLoader } from './useLoader';

export interface CheckInController extends Loader<CheckInBoard> {
  action: Action;
  handleCheckIn: () => Promise<void>;
}

export function useCheckIn(token: string, contractId: number): CheckInController {
  const action = useAction();
  const loader = useLoader(
    () => checkInApi.board(token, contractId),
    () => false,
    '',
    `checkin|${contractId}`,
  );
  const { handleReload } = loader;
  const handleCheckIn = useCallback(
    () =>
      action.run(
        async () => checkInApi.checkIn(token, contractId, await currentPosition()),
        '¡Listo! Quedó registrado que llegaste.',
        handleReload,
      ),
    [action, contractId, handleReload, token],
  );
  return { ...loader, action, handleCheckIn };
}

export interface VenueLocationController {
  action: Action;
  handleSaveHere: () => Promise<void>;
}

/** El dueño, parado en su establecimiento, guarda su ubicación para el check-in. */
export function useVenueLocation(
  token: string,
  venueId: number,
  onDone: () => void,
): VenueLocationController {
  const action = useAction();
  const handleSaveHere = useCallback(
    () =>
      action.run(
        async () => checkInApi.setVenueLocation(token, venueId, await currentPosition()),
        'Ubicación de la cancha guardada.',
        onDone,
      ),
    [action, onDone, token, venueId],
  );
  return { action, handleSaveHere };
}
