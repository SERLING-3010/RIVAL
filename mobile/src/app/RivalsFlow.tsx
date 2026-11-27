// Búsqueda de rivales (Sprints 2, 11 y 12) y rivales sugeridos con motivos (Sprint 18).

import { useRivalSearch } from '../controllers/useScouting';
import { useSuggestions } from '../controllers/useSuggestions';
import { moderationApi } from '../services/moderationApi';
import { RivalSearchScreen } from '../ui/screens/RivalSearchScreen';
import { SuggestionsScreen } from '../ui/screens/SuggestionsScreen';
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

export function Suggestions({
  token,
  navigator,
  teamId,
  isAdmin,
}: MatchCtx & { teamId: number; isAdmin: boolean }) {
  return (
    <SuggestionsScreen
      controller={useSuggestions(token, teamId)}
      canChallenge={isAdmin}
      onChallenge={(target) => navigator.push({ name: 'createMatchRequest', teamId, targetTeamId: target })}
      onBack={navigator.goBack}
    />
  );
}
