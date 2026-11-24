// Elige la pantalla de los Sprints 2 y 3 según la ruta actual.

import type { ReactNode } from 'react';

import type { Route } from '../controllers/useNavigator';
import { Activity, ContractDetail, Contracts, ProposeContract } from './ContractFlow';
import type { MatchCtx } from './MatchFlow';
import {
  CreateRequest,
  Feed,
  FreeAgentPanel,
  FreeAgentSearch,
  Offer,
  Offers,
  Requests,
  Rivals,
} from './MatchFlow';

/** Devuelve la pantalla de partidos para la ruta, o null si la ruta no es de este flujo. */
export function renderMatchRoute(route: Route, ctx: MatchCtx): ReactNode | null {
  switch (route.name) {
    case 'rivals':
      return <Rivals {...ctx} teamId={route.teamId} isAdmin={route.isAdmin} />;
    case 'freeAgentPanel':
      return <FreeAgentPanel {...ctx} />;
    case 'freeAgentSearch':
      return <FreeAgentSearch {...ctx} team={route.team} />;
    case 'matchRequests':
      return <Requests {...ctx} teamId={route.teamId} isAdmin={route.isAdmin} />;
    case 'createMatchRequest':
      return <CreateRequest {...ctx} teamId={route.teamId} targetTeamId={route.targetTeamId} />;
    case 'matchFeed':
      return <Feed {...ctx} teamId={route.teamId} isAdmin={route.isAdmin} />;
    case 'makeOffer':
      return <Offer {...ctx} teamId={route.teamId} request={route.request} />;
    case 'offers':
      return (
        <Offers
          {...ctx}
          requestId={route.requestId}
          isRequestAdmin={route.isRequestAdmin}
          myTeamIds={route.myTeamIds}
          requestOpen={route.requestOpen}
        />
      );
    case 'contracts':
      return <Contracts {...ctx} teamId={route.teamId} />;
    case 'contract':
      return <ContractDetail {...ctx} contractId={route.contractId} />;
    case 'proposeContract':
      return <ProposeContract {...ctx} contract={route.contract} />;
    case 'activity':
      return <Activity {...ctx} scope={route.scope} id={route.id} title={route.title} />;
    default:
      return null;
  }
}
