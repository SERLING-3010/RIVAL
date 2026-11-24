// Composición de los Sprints 5 y 8: ligas, crear liga, detalle, calendario y tabla, y partidos del árbitro.

import { useCreateLeague } from '../controllers/useCreateLeague';
import { useLeague, useLeagueHome } from '../controllers/useLeagues';
import { useMyTeams } from '../controllers/useMyTeams';
import { useRefereeMatches, useSeason } from '../controllers/useSeason';
import type { RefereeEntry } from '../domain/leagueModels';
import type { MyTeam } from '../domain/models';
import { CreateLeagueScreen } from '../ui/screens/CreateLeagueScreen';
import { LeagueScreen } from '../ui/screens/LeagueScreen';
import { LeaguesScreen } from '../ui/screens/LeaguesScreen';
import { RefereeMatchesScreen } from '../ui/screens/RefereeMatchesScreen';
import { SeasonScreen } from '../ui/screens/SeasonScreen';
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
  const controller = useLeague(token, leagueId);
  return (
    <LeagueScreen
      controller={controller}
      user={user}
      myTeams={useTeamsOrEmpty(token)}
      onSeason={(canManage) =>
        navigator.push({
          name: 'season',
          leagueId,
          canManage,
          referees: controller.state.kind === 'success' ? controller.state.data.referees : [],
        })
      }
      onBack={navigator.goBack}
    />
  );
}

export function Season({
  token,
  navigator,
  leagueId,
  canManage,
  referees,
}: MatchCtx & { leagueId: number; canManage: boolean; referees: RefereeEntry[] }) {
  return (
    <SeasonScreen
      controller={useSeason(token, leagueId)}
      canManage={canManage}
      referees={referees}
      onBack={navigator.goBack}
    />
  );
}

export function RefereeMatches({ token, navigator }: MatchCtx) {
  return <RefereeMatchesScreen controller={useRefereeMatches(token)} onBack={navigator.goBack} />;
}
