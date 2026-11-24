// Panel del jugador: aparecer como agente libre por deporte y responder invitaciones.

import { useCallback } from 'react';

import type { FreeAgentProfile, Invitation } from '../domain/matchModels';
import { scoutingApi } from '../services/scoutingApi';
import type { Action } from './useAction';
import { useAction } from './useAction';
import type { Loader } from './useLoader';
import { useLoader } from './useLoader';

export interface FreeAgentPanelController {
  profiles: Loader<FreeAgentProfile[]>;
  invitations: Loader<Invitation[]>;
  action: Action;
  handleToggle: (sportCode: string, active: boolean, current: FreeAgentProfile | undefined) => Promise<void>;
  handleRespond: (invitationId: number, accept: boolean) => Promise<void>;
}

export function useFreeAgentPanel(token: string): FreeAgentPanelController {
  const action = useAction();
  const profiles = useLoader(
    () => scoutingApi.myFreeAgent(token),
    () => false,
    '',
    `profiles|${token}`,
  );
  const invitations = useLoader(
    () => scoutingApi.myInvitations(token),
    (items) => items.length === 0,
    'No tienes invitaciones pendientes.',
    `invitations|${token}`,
  );
  const { handleReload: reloadProfiles } = profiles;
  const { handleReload: reloadInvitations } = invitations;

  const handleToggle = useCallback(
    (sportCode: string, active: boolean, current: FreeAgentProfile | undefined) =>
      action.run(
        () =>
          scoutingApi.setFreeAgent(token, {
            sport_code: sportCode,
            active,
            position: current?.position ?? null,
            note: current?.note ?? null,
          }),
        active ? 'Ahora apareces como agente libre.' : 'Ya no apareces como agente libre.',
        reloadProfiles,
      ),
    [action, reloadProfiles, token],
  );

  const handleRespond = useCallback(
    (invitationId: number, accept: boolean) =>
      action.run(
        () => scoutingApi.respondInvitation(token, invitationId, accept),
        accept ? '¡Bienvenido al equipo!' : 'Invitación rechazada.',
        () => {
          reloadInvitations();
          reloadProfiles();
        },
      ),
    [action, reloadInvitations, reloadProfiles, token],
  );

  return { profiles, invitations, action, handleToggle, handleRespond };
}
