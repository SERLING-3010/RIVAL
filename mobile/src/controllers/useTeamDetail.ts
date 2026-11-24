// Mi equipo: plantilla, solicitudes pendientes (solo administrador), capitán y salir.

import { useCallback, useEffect, useState } from 'react';

import { errorToViewState, toAppError } from '../domain/appError';
import type { JoinRequest, TeamDetail } from '../domain/models';
import type { ViewState } from '../domain/viewState';
import { successOrEmpty } from '../domain/viewState';
import { teamApi } from '../services/teamApi';
import { useSubmitLock } from './useSubmitLock';

export interface TeamDetailController {
  detail: ViewState<TeamDetail>;
  requests: ViewState<JoinRequest[]>;
  isAdmin: boolean;
  busy: boolean;
  actionMessage: string | null;
  handleRefresh: () => void;
  handleDecide: (requestId: number, approve: boolean) => Promise<void>;
  handleSetCaptain: (userId: number) => Promise<void>;
  handleLeave: () => Promise<void>;
}

export function useTeamDetail(
  token: string,
  userId: number,
  teamId: number,
  onLeft: () => void,
): TeamDetailController {
  const [detail, setDetail] = useState<ViewState<TeamDetail>>({ kind: 'loading' });
  const [requests, setRequests] = useState<ViewState<JoinRequest[]>>({ kind: 'loading' });
  const [busy, setBusy] = useState(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);
  const lock = useSubmitLock();

  const isAdmin = detail.kind === 'success' && detail.data.admin_user_id === userId;

  useEffect(() => {
    let active = true;
    setDetail({ kind: 'loading' });
    teamApi
      .detail(token, teamId)
      .then(async (data) => {
        if (!active) return;
        setDetail({ kind: 'success', data });
        if (data.admin_user_id !== userId) return;
        try {
          const pending = await teamApi.pendingRequests(token, teamId);
          if (active)
            setRequests(successOrEmpty(pending, pending.length === 0, 'No hay solicitudes pendientes.'));
        } catch (error) {
          if (active) setRequests(errorToViewState<JoinRequest[]>(error));
        }
      })
      .catch((error: unknown) => {
        if (active) setDetail(errorToViewState<TeamDetail>(error));
      });
    return () => {
      active = false;
    };
  }, [token, teamId, userId, attempt]);

  const run = useCallback(
    async (action: () => Promise<unknown>, success: string) => {
      await lock(async () => {
        setBusy(true);
        setActionMessage(null);
        try {
          await action();
          setActionMessage(success);
          setAttempt((n) => n + 1);
        } catch (error) {
          setActionMessage(toAppError(error).message);
        } finally {
          setBusy(false);
        }
      });
    },
    [lock],
  );

  return {
    detail,
    requests,
    isAdmin,
    busy,
    actionMessage,
    handleRefresh: useCallback(() => setAttempt((n) => n + 1), []),
    handleDecide: (requestId, approve) =>
      run(
        () => teamApi.decide(token, requestId, approve),
        approve ? 'Jugador aceptado.' : 'Solicitud rechazada.',
      ),
    handleSetCaptain: (memberId) =>
      run(() => teamApi.setCaptain(token, teamId, memberId), 'Capitán actualizado.'),
    handleLeave: () =>
      lock(async () => {
        setBusy(true);
        try {
          await teamApi.leave(token, teamId);
          onLeft();
        } catch (error) {
          setActionMessage(toAppError(error).message);
        } finally {
          setBusy(false);
        }
      }).then(() => undefined),
  };
}
