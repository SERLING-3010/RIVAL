// Composición con sesión: inicio por rol, buscar y crear equipo, Mi equipo.

import { useCatalog } from '../controllers/useCatalog';
import { renderMatchRoute } from './MatchRoutes';
import { TeamActions } from './TeamActions';
import { useCreateTeamForm } from '../controllers/useCreateTeamForm';
import { useMyTeams } from '../controllers/useMyTeams';
import type { Navigator } from '../controllers/useNavigator';
import type { Session } from '../controllers/useSession';
import { useTeamDetail } from '../controllers/useTeamDetail';
import { useTeamSearch } from '../controllers/useTeamSearch';
import type { Sport, User } from '../domain/models';
import { Screen } from '../ui/components/Screen';
import { StateView } from '../ui/components/StateView';
import { CreateTeamScreen } from '../ui/screens/CreateTeamScreen';
import { HomeScreen } from '../ui/screens/HomeScreen';
import { TeamScreen } from '../ui/screens/TeamScreen';
import { TeamSearchScreen } from '../ui/screens/TeamSearchScreen';

interface Props {
  session: Session;
  user: User;
  token: string;
  navigator: Navigator;
}

interface Ctx extends Props {
  sports: Sport[];
}

function HomeContainer({ session, user, token, navigator }: Ctx) {
  const teams = useMyTeams(token);
  return (
    <HomeScreen
      user={user}
      myTeams={teams.state}
      onRefreshTeams={teams.handleRefresh}
      onSearchTeam={() => navigator.push({ name: 'teamSearch' })}
      onCreateTeam={() => navigator.push({ name: 'createTeam' })}
      onFreeAgent={() => navigator.push({ name: 'freeAgentPanel' })}
      onLeagues={() => navigator.push({ name: 'leagues' })}
      onMyVenues={() => navigator.push({ name: 'myVenues' })}
      onTransferOffers={() => navigator.push({ name: 'transferOffers' })}
      onOpenTeam={(teamId) => navigator.push({ name: 'team', teamId })}
      onLogout={() => void session.handleLogout()}
    />
  );
}

function SearchContainer({ user, token, navigator, sports }: Ctx) {
  const controller = useTeamSearch(token, user.city);
  return (
    <TeamSearchScreen
      controller={controller}
      sports={sports}
      canJoinAsCoach={user.roles.includes('COACH')}
      onCreateTeam={() => navigator.push({ name: 'createTeam' })}
      onBack={navigator.goBack}
    />
  );
}

function CreateContainer({ user, token, navigator, sports }: Ctx) {
  const controller = useCreateTeamForm(token, user, (teamId) => {
    navigator.reset({ name: 'home' });
    navigator.push({ name: 'team', teamId });
  });
  return (
    <CreateTeamScreen
      controller={controller}
      sports={sports}
      isCoach={user.roles.includes('COACH')}
      onBack={navigator.goBack}
    />
  );
}

function TeamContainer({ user, token, navigator, teamId }: Ctx & { teamId: number }) {
  const controller = useTeamDetail(token, user.id, teamId, () => navigator.reset({ name: 'home' }));
  return (
    <TeamScreen
      controller={controller}
      userId={user.id}
      onBack={navigator.goBack}
      renderActions={(team, isAdmin) => <TeamActions team={team} isAdmin={isAdmin} navigator={navigator} />}
    />
  );
}

export function SignedInFlow(props: Props) {
  const catalog = useCatalog();
  const route = props.navigator.current;
  if (
    route.name === 'home' ||
    route.name === 'rolePicker' ||
    route.name === 'register' ||
    route.name === 'login'
  ) {
    return <HomeContainer {...props} sports={[]} />;
  }
  return (
    <StateView state={catalog.state} onRetry={catalog.handleRetry}>
      {(sports) => {
        if (route.name === 'teamSearch') return <SearchContainer {...props} sports={sports} />;
        if (route.name === 'createTeam') return <CreateContainer {...props} sports={sports} />;
        if (route.name === 'team') return <TeamContainer {...props} sports={sports} teamId={route.teamId} />;
        return renderMatchRoute(route, { ...props, sports });
      }}
    </StateView>
  );
}

export function LoadingScreen() {
  return (
    <Screen title="RIVAL">
      <StateView state={{ kind: 'loading' }}>{() => null}</StateView>
    </Screen>
  );
}
