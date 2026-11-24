// Elige la pantalla de partidos, ligas, establecimientos y modo manager (Sprints 2 a 7) según la ruta.

import type { ReactNode } from 'react';

import type { Route } from '../controllers/useNavigator';
import { Activity, ContractDetail, Contracts, ProposeContract } from './ContractFlow';
import { CreateLeague, LeagueDetail, Leagues, RefereeMatches, Season } from './LeagueFlow';
import { Lineup, Manager, Market, PlayerCardRoute, TransferOffers } from './ManagerFlow';
import type { MatchCtx } from './MatchFlow';
import { BookVenue, CreateVenue, MyVenues, VenueDetail } from './VenueFlow';
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
    case 'leagues':
      return <Leagues {...ctx} />;
    case 'createLeague':
      return <CreateLeague {...ctx} />;
    case 'league':
      return <LeagueDetail {...ctx} leagueId={route.leagueId} />;
    case 'myVenues':
      return <MyVenues {...ctx} />;
    case 'createVenue':
      return <CreateVenue {...ctx} />;
    case 'venue':
      return <VenueDetail {...ctx} venueId={route.venueId} match={route.match} />;
    case 'bookVenue':
      return <BookVenue {...ctx} match={route.match} city={route.city} />;
    case 'manager':
      return <Manager {...ctx} teamId={route.teamId} />;
    case 'market':
      return (
        <Market
          {...ctx}
          teamId={route.teamId}
          sport={route.sport}
          city={route.city}
          balance={route.balance}
        />
      );
    case 'playerCard':
      return <PlayerCardRoute {...ctx} userId={route.userId} />;
    case 'transferOffers':
      return <TransferOffers {...ctx} />;
    case 'lineup':
      return (
        <Lineup {...ctx} contractId={route.contractId} teamId={route.teamId} teamScore={route.teamScore} />
      );
    case 'season':
      return (
        <Season {...ctx} leagueId={route.leagueId} canManage={route.canManage} referees={route.referees} />
      );
    case 'refereeMatches':
      return <RefereeMatches {...ctx} />;
    default:
      return null;
  }
}
