// Navegación simple por pila, sin dependencias nativas extra. El estado vive aquí, no en las vistas.

import { useCallback, useState } from 'react';

import type { Contract } from '../domain/contractModels';
import type { RefereeEntry } from '../domain/leagueModels';
import type { MatchRequest } from '../domain/matchModels';
import type { ReportTarget } from '../domain/moderationModels';
import type { MatchToBook } from '../domain/venueModels';
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
  | { name: 'activity'; scope: 'contracts' | 'teams'; id: number; title: string }
  | { name: 'leagues' }
  | { name: 'createLeague' }
  | { name: 'league'; leagueId: number }
  | { name: 'myVenues' }
  | { name: 'createVenue' }
  | { name: 'venue'; venueId: number; match: MatchToBook | null }
  | { name: 'bookVenue'; match: MatchToBook; city: string }
  | { name: 'manager'; teamId: number }
  | { name: 'market'; teamId: number; sport: string; city: string; balance: number }
  | { name: 'playerCard'; userId: number }
  | { name: 'transferOffers' }
  | { name: 'lineup'; contractId: number; teamId: number; teamScore: number }
  | { name: 'season'; leagueId: number; canManage: boolean; referees: RefereeEntry[] }
  | { name: 'refereeMatches' }
  | { name: 'callup'; contractId: number; teamId: number; isAdmin: boolean }
  | { name: 'rate'; contractId: number }
  | { name: 'myCallups' }
  | { name: 'pending' }
  | { name: 'report'; target: ReportTarget }
  | { name: 'mySanctions' }
  | { name: 'moderation' }
  | { name: 'blockedTeams'; teamId: number }
  | { name: 'loanRequest'; contractId: number; teamId: number; rivalId: number }
  | { name: 'loans' };

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
