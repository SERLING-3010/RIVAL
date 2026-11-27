// Préstamos: los que esperan mi decisión y pedir un jugador prestado para un partido.

import { useCallback, useState } from 'react';

import type { Loan } from '../domain/loanModels';
import type { Rival } from '../domain/matchModels';
import type { TeamDetail } from '../domain/models';
import type { LoanDecision } from '../services/loanApi';
import { loanApi } from '../services/loanApi';
import { scoutingApi } from '../services/scoutingApi';
import { teamApi } from '../services/teamApi';
import type { Action } from './useAction';
import { useAction } from './useAction';
import type { Loader } from './useLoader';
import { useLoader } from './useLoader';

const MESSAGE: Record<LoanDecision, string> = {
  'owner-accept': 'Aceptaste. Ahora decide el jugador.',
  'owner-reject': 'Préstamo rechazado.',
  'player-accept': '¡Listo! Juegas prestado ese partido.',
  'player-reject': 'Rechazaste el préstamo.',
  cancel: 'Préstamo cancelado.',
};

export interface MyLoansController extends Loader<Loan[]> {
  action: Action;
  handleDecide: (loanId: number, decision: LoanDecision) => Promise<void>;
}

export function useMyLoans(token: string): MyLoansController {
  const action = useAction();
  const loader = useLoader(
    () => loanApi.mine(token),
    (items) => items.length === 0,
    'No tienes préstamos por decidir.',
    'my-loans',
  );
  const { handleReload } = loader;
  const handleDecide = useCallback(
    (loanId: number, decision: LoanDecision) =>
      action.run(() => loanApi.decide(token, loanId, decision), MESSAGE[decision], handleReload),
    [action, handleReload, token],
  );
  return { ...loader, action, handleDecide };
}

export interface LoanRequestController {
  current: Loader<Loan[]>;
  teams: Loader<Rival[]>;
  squad: Loader<TeamDetail> | null;
  selectedTeam: number | null;
  action: Action;
  handleSelectTeam: (teamId: number | null) => void;
  handleRequest: (playerId: number) => Promise<void>;
}

export function useLoanRequest(
  token: string,
  contractId: number,
  myTeamId: number,
  rivalId: number,
): LoanRequestController {
  const [selectedTeam, setSelectedTeam] = useState<number | null>(null);
  const action = useAction();
  const current = useLoader(
    () => loanApi.forContract(token, contractId),
    () => false,
    '',
    `loans|${contractId}`,
  );
  const teams = useLoader(
    () =>
      scoutingApi
        .rivals(token, myTeamId, 'CITY', 5, 1)
        .then((p) => p.items.filter((r) => r.team.id !== rivalId)),
    (items) => items.length === 0,
    'No hay otros equipos de tu deporte en la ciudad.',
    `loan-teams|${myTeamId}|${rivalId}`,
  );
  const squad = useLoader(
    () =>
      selectedTeam === null ? Promise.reject(new Error('sin equipo')) : teamApi.detail(token, selectedTeam),
    () => false,
    '',
    `loan-squad|${selectedTeam ?? 'none'}`,
  );
  const { handleReload } = current;
  const handleRequest = useCallback(
    (playerId: number) =>
      selectedTeam === null
        ? Promise.resolve()
        : action.run(
            () => loanApi.request(token, contractId, playerId, selectedTeam),
            'Préstamo pedido. Primero decide su DT y después el jugador.',
            handleReload,
          ),
    [action, contractId, handleReload, selectedTeam, token],
  );
  return {
    current,
    teams,
    squad: selectedTeam === null ? null : squad,
    selectedTeam,
    action,
    handleSelectTeam: setSelectedTeam,
    handleRequest,
  };
}
