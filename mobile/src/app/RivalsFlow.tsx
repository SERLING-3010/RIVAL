// Búsqueda de rivales (Sprints 2, 11 y 12): retar, ordenar por nivel, reportar y bloquear.

import { useRivalSearch } from '../controllers/useScouting';
import { moderationApi } from '../services/moderationApi';
import { RivalSearchScreen } from '../ui/screens/RivalSearchScreen';
import type { MatchCtx } from './MatchFlow';

export function Rivals({
  token,
  navigator,
  teamId,
  isAdmin,
}: MatchCtx & { teamId: number; isAdmin: boolean }) {
  const controller = useRivalSearch(token, teamId);
  return (
    <RivalSearchScreen
      controller={controller}
      canChallenge={isAdmin}
      onBack={navigator.goBack}
      onChallenge={(target) => navigator.push({ name: 'createMatchRequest', teamId, targetTeamId: target })}
      onReport={(team) =>
        navigator.push({ name: 'report', target: { kind: 'team', id: team.id, name: team.name } })
      }
      onBlock={(other) =>
        void moderationApi.block(token, teamId, other).then(controller.handleReload, controller.handleReload)
      }
    />
  );
}
