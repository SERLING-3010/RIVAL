// Composición del Sprint 5: ligas, crear liga y detalle con inscripción y cuerpo arbitral.

import { useCreateLeague } from '../controllers/useCreateLeague';
import { useLeague, useLeagueHome } from '../controllers/useLeagues';
import { useMyTeams } from '../controllers/useMyTeams';
import type { MyTeam } from '../domain/models';
import { CreateLeagueScreen } from '../ui/screens/CreateLeagueScreen';
import { LeagueScreen } from '../ui/screens/LeagueScreen';
import { LeaguesScreen } from '../ui/screens/LeaguesScreen';
import type { MatchCtx } from './MatchFlow';

function useTeamsOrEmpty(token: string): MyTeam[] {
  const teams = useMyTeams(token);
  return teams.state.kind === 'success' ? teams.state.data : [];
}

export function Leagues({ token, navigator, user }: MatchCtx) {
  const teams = useTeamsOrEmpty(token);
  return (
    <LeaguesScreen
      controller={useLeagueHome(token, user)}
      canCreate={user.roles.includes('REFEREE') || teams.length > 0}
      onOpen={(leagueId) => navigator.push({ name: 'league', leagueId })}
      onCreate={() => navigator.push({ name: 'createLeague' })}
      onBack={navigator.goBack}
    />
  );
}

export function CreateLeague({ token, navigator, user, sports }: MatchCtx) {
  const controller = useCreateLeague(token, user, (leagueId) => {
    navigator.goBack();
    navigator.push({ name: 'league', leagueId });
  });
  return <CreateLeagueScreen controller={controller} sports={sports} onBack={navigator.goBack} />;
}

export function LeagueDetail({ token, navigator, user, leagueId }: MatchCtx & { leagueId: number }) {
  return (
    <LeagueScreen
      controller={useLeague(token, leagueId)}
      user={user}
      myTeams={useTeamsOrEmpty(token)}
      onBack={navigator.goBack}
    />
  );
}
