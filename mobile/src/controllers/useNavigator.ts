// Navegación simple por pila, sin dependencias nativas extra. El estado vive aquí, no en las vistas.

import { useCallback, useState } from 'react';

import type { Contract } from '../domain/contractModels';
import type { MatchRequest } from '../domain/matchModels';
import type { TeamSummary, UserRole } from '../domain/models';

export type Route =
  | { name: 'rolePicker' }
  | { name: 'register'; role: UserRole }
  | { name: 'login' }
  | { name: 'home' }
  | { name: 'teamSearch' }
  | { name: 'createTeam' }
  | { name: 'team'; teamId: number }
  | { name: 'rivals'; teamId: number; isAdmin: boolean }
  | { name: 'freeAgentPanel' }
  | { name: 'freeAgentSearch'; team: TeamSummary }
  | { name: 'matchRequests'; teamId: number; isAdmin: boolean }
  | { name: 'createMatchRequest'; teamId: number; targetTeamId: number | null }
  | { name: 'matchFeed'; teamId: number; isAdmin: boolean }
  | { name: 'makeOffer'; teamId: number; request: MatchRequest }
  | { name: 'offers'; requestId: number; isRequestAdmin: boolean; myTeamIds: number[]; requestOpen: boolean }
  | { name: 'contracts'; teamId: number }
  | { name: 'contract'; contractId: number }
  | { name: 'proposeContract'; contract: Contract }
  | { name: 'activity'; scope: 'contracts' | 'teams'; id: number; title: string };

export interface Navigator {
  current: Route;
  canGoBack: boolean;
  push: (route: Route) => void;
  goBack: () => void;
  reset: (route: Route) => void;
}

export function useNavigator(initial: Route): Navigator {
  const [stack, setStack] = useState<Route[]>([initial]);
  const push = useCallback((route: Route) => setStack((s) => [...s, route]), []);
  const goBack = useCallback(() => setStack((s) => (s.length > 1 ? s.slice(0, -1) : s)), []);
  const reset = useCallback((route: Route) => setStack([route]), []);
  return {
    current: stack[stack.length - 1] ?? initial,
    canGoBack: stack.length > 1,
    push,
    goBack,
    reset,
  };
}
