// Composición del Sprint 2: rivales, agentes libres, búsquedas de partido y ofertas.

import { useFreeAgentPanel } from '../controllers/useFreeAgentPanel';
import { useCreateMatchRequest, useOfferForm } from '../controllers/useMatchForms';
import { useMatchFeed, useMyMatchRequests, useOffers } from '../controllers/useMatches';
import type { Navigator } from '../controllers/useNavigator';
import { useFreeAgentSearch, useRivalSearch } from '../controllers/useScouting';
import type { MatchRequest } from '../domain/matchModels';
import type { Sport, TeamSummary, User } from '../domain/models';
import { CreateMatchRequestScreen } from '../ui/screens/CreateMatchRequestScreen';
import { FreeAgentPanelScreen } from '../ui/screens/FreeAgentPanelScreen';
import { FreeAgentSearchScreen } from '../ui/screens/FreeAgentSearchScreen';
import { MakeOfferScreen } from '../ui/screens/MakeOfferScreen';
import { MatchFeedScreen } from '../ui/screens/MatchFeedScreen';
import { MatchRequestsScreen } from '../ui/screens/MatchRequestsScreen';
import { OffersScreen } from '../ui/screens/OffersScreen';
import { RivalSearchScreen } from '../ui/screens/RivalSearchScreen';

export interface MatchCtx {
  user: User;
  token: string;
  navigator: Navigator;
  sports: Sport[];
}

export function Rivals({
  token,
  navigator,
  teamId,
  isAdmin,
}: MatchCtx & { teamId: number; isAdmin: boolean }) {
  return (
    <RivalSearchScreen
      controller={useRivalSearch(token, teamId)}
      canChallenge={isAdmin}
      onBack={navigator.goBack}
      onChallenge={(target) => navigator.push({ name: 'createMatchRequest', teamId, targetTeamId: target })}
    />
  );
}

export function FreeAgentPanel({ token, navigator, sports, user }: MatchCtx) {
  return (
    <FreeAgentPanelScreen
      controller={useFreeAgentPanel(token)}
      sports={sports}
      mySports={user.sports}
      onBack={navigator.goBack}
    />
  );
}

export function FreeAgentSearch({ token, navigator, team }: MatchCtx & { team: TeamSummary }) {
  return <FreeAgentSearchScreen controller={useFreeAgentSearch(token, team)} onBack={navigator.goBack} />;
}

export function Requests({
  token,
  navigator,
  teamId,
  isAdmin,
}: MatchCtx & { teamId: number; isAdmin: boolean }) {
  return (
    <MatchRequestsScreen
      controller={useMyMatchRequests(token, teamId)}
      isAdmin={isAdmin}
      onBack={navigator.goBack}
      onCreate={() => navigator.push({ name: 'createMatchRequest', teamId, targetTeamId: null })}
      onOpenOffers={(requestId, open) =>
        navigator.push({
          name: 'offers',
          requestId,
          isRequestAdmin: isAdmin,
          myTeamIds: [teamId],
          requestOpen: open,
        })
      }
    />
  );
}

export function CreateRequest({
  token,
  navigator,
  teamId,
  targetTeamId,
}: MatchCtx & { teamId: number; targetTeamId: number | null }) {
  const controller = useCreateMatchRequest(token, teamId, targetTeamId, () => {
    navigator.goBack();
    if (targetTeamId === null) return;
    navigator.push({ name: 'matchRequests', teamId, isAdmin: true });
  });
  return (
    <CreateMatchRequestScreen
      controller={controller}
      isChallenge={targetTeamId !== null}
      onBack={navigator.goBack}
    />
  );
}

export function Feed({ token, navigator, teamId, isAdmin }: MatchCtx & { teamId: number; isAdmin: boolean }) {
  return (
    <MatchFeedScreen
      controller={useMatchFeed(token, teamId)}
      isAdmin={isAdmin}
      onBack={navigator.goBack}
      onOffer={(request) => navigator.push({ name: 'makeOffer', teamId, request })}
      onMyOffers={(request) =>
        navigator.push({
          name: 'offers',
          requestId: request.id,
          isRequestAdmin: false,
          myTeamIds: [teamId],
          requestOpen: true,
        })
      }
    />
  );
}

export function Offer({
  token,
  navigator,
  teamId,
  request,
}: MatchCtx & { teamId: number; request: MatchRequest }) {
  const controller = useOfferForm(token, teamId, request, navigator.goBack);
  return <MakeOfferScreen controller={controller} request={request} onBack={navigator.goBack} />;
}

export function Offers(
  props: MatchCtx & { requestId: number; isRequestAdmin: boolean; myTeamIds: number[]; requestOpen: boolean },
) {
  return (
    <OffersScreen
      controller={useOffers(props.token, props.requestId)}
      isRequestAdmin={props.isRequestAdmin}
      myTeamIds={props.myTeamIds}
      requestOpen={props.requestOpen}
      onBack={props.navigator.goBack}
    />
  );
}
