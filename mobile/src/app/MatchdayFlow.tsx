// Composición del Sprint 10: convocatoria, valorar compañeros y mis convocatorias.

import { useTeamManager } from '../controllers/useManager';
import { useCallUp, useMyCallUps, useRatings } from '../controllers/useMatchday';
import { CallUpScreen } from '../ui/screens/CallUpScreen';
import { MyCallUpsScreen } from '../ui/screens/MyCallUpsScreen';
import { RateTeammatesScreen } from '../ui/screens/RateTeammatesScreen';
import type { MatchCtx } from './MatchFlow';

export function CallUp({
  token,
  navigator,
  user,
  contractId,
  teamId,
  isAdmin,
}: MatchCtx & { contractId: number; teamId: number; isAdmin: boolean }) {
  const manager = useTeamManager(token, teamId);
  return (
    <CallUpScreen
      controller={useCallUp(token, contractId)}
      squad={manager.state.kind === 'success' ? manager.state.data.squad : []}
      isAdmin={isAdmin}
      myUserId={user.id}
      onBack={navigator.goBack}
    />
  );
}

export function RateTeammates({ token, navigator, contractId }: MatchCtx & { contractId: number }) {
  return <RateTeammatesScreen controller={useRatings(token, contractId)} onBack={navigator.goBack} />;
}

export function MyCallUps({ token, navigator }: MatchCtx) {
  return (
    <MyCallUpsScreen
      controller={useMyCallUps(token)}
      onOpen={(contractId) => navigator.push({ name: 'contract', contractId })}
      onBack={navigator.goBack}
    />
  );
}
