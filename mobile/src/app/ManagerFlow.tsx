// Composición del Sprint 7: modo manager, mercado, ficha, ofertas del jugador y planilla.

import { useLineup } from '../controllers/useLineup';
import { useMarket, useMyTransferOffers, usePlayerCard, useTeamManager } from '../controllers/useManager';
import type { SquadMember } from '../domain/managerModels';
import type { ViewState } from '../domain/viewState';
import { LineupScreen } from '../ui/screens/LineupScreen';
import { ManagerScreen } from '../ui/screens/ManagerScreen';
import { MarketScreen } from '../ui/screens/MarketScreen';
import { PlayerCardScreen } from '../ui/screens/PlayerCardScreen';
import { TransferOffersScreen } from '../ui/screens/TransferOffersScreen';
import type { MatchCtx } from './MatchFlow';

export function Manager({ token, navigator, teamId }: MatchCtx & { teamId: number }) {
  const controller = useTeamManager(token, teamId);
  const team = controller.state.kind === 'success' ? controller.state.data.team : null;
  return (
    <ManagerScreen
      controller={controller}
      onOpenCard={(userId) => navigator.push({ name: 'playerCard', userId })}
      onMarket={(balance) =>
        team && navigator.push({ name: 'market', teamId, sport: team.sport_code, city: team.city, balance })
      }
      onBack={navigator.goBack}
    />
  );
}

export function Market({
  token,
  navigator,
  teamId,
  sport,
  city,
  balance,
}: MatchCtx & { teamId: number; sport: string; city: string; balance: number }) {
  return (
    <MarketScreen
      controller={useMarket(token, teamId, sport, city)}
      balance={balance}
      onOpenCard={(userId) => navigator.push({ name: 'playerCard', userId })}
      onBack={navigator.goBack}
    />
  );
}

export function PlayerCardRoute({ token, navigator, userId }: MatchCtx & { userId: number }) {
  return <PlayerCardScreen controller={usePlayerCard(token, userId)} onBack={navigator.goBack} />;
}

export function TransferOffers({ token, navigator }: MatchCtx) {
  return <TransferOffersScreen controller={useMyTransferOffers(token)} onBack={navigator.goBack} />;
}

export function Lineup({
  token,
  navigator,
  contractId,
  teamId,
  teamScore,
}: MatchCtx & { contractId: number; teamId: number; teamScore: number }) {
  const manager = useTeamManager(token, teamId);
  const squad: ViewState<SquadMember[]> =
    manager.state.kind === 'success' ? { kind: 'success', data: manager.state.data.squad } : manager.state;
  return (
    <LineupScreen
      controller={useLineup(token, contractId, teamScore, navigator.goBack)}
      squad={squad}
      teamScore={teamScore}
      onRetry={manager.handleReload}
      onBack={navigator.goBack}
    />
  );
}
