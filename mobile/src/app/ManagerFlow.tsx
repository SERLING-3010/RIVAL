// Composición del Sprint 7: modo manager, mercado, ficha, ofertas del jugador y planilla.

import { useBadges } from '../controllers/useBadges';
import { useNewCard } from '../controllers/useNewCard';
import { useSquad } from '../controllers/useSquad';
import { seenKey } from '../domain/newCards';
import { useLineup } from '../controllers/useLineup';
import { useMarket, useMyTransferOffers, usePlayerCard, useTeamManager } from '../controllers/useManager';
import type { SquadMember } from '../domain/managerModels';
import type { ViewState } from '../domain/viewState';
import { LineupScreen } from '../ui/screens/LineupScreen';
import { ManagerScreen } from '../ui/screens/ManagerScreen';
import { MarketScreen } from '../ui/screens/MarketScreen';
import { PlayerCardScreen } from '../ui/screens/PlayerCardScreen';
import { TransferOffersScreen } from '../ui/screens/TransferOffersScreen';
import type { BadgeOwner } from '../domain/badgeModels';
import { BadgesScreen } from '../ui/screens/BadgesScreen';
import { SquadScreen } from '../ui/screens/SquadScreen';
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

export function PlayerCardRoute({ token, navigator, userId, user }: MatchCtx & { userId: number }) {
  const controller = usePlayerCard(token, userId);
  const own = userId === user.id; // la celebración es solo para la carta propia
  const specials = controller.state.kind === 'success' ? controller.state.data.card.specials : null;
  const newCard = useNewCard(own ? seenKey('player', userId, user.id) : null, specials);
  return (
    <PlayerCardScreen
      controller={controller}
      newCard={newCard}
      onReport={(id, name) => navigator.push({ name: 'report', target: { kind: 'user', id, name } })}
      onBadges={(id, name) =>
        navigator.push({ name: 'badges', owner: 'player', id, title: `Insignias de ${name}` })
      }
      onBack={navigator.goBack}
    />
  );
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

export function Badges({
  token,
  navigator,
  owner,
  id,
  title,
}: MatchCtx & { owner: BadgeOwner; id: number; title: string }) {
  return <BadgesScreen title={title} controller={useBadges(token, owner, id)} onBack={navigator.goBack} />;
}

export function SquadRoute({ token, navigator, teamId, user }: MatchCtx & { teamId: number }) {
  const controller = useSquad(token, teamId);
  const specials =
    controller.state.kind === 'success' ? (controller.state.data.card?.specials ?? null) : null;
  const newCard = useNewCard(seenKey('team', teamId, user.id), specials);
  return (
    <SquadScreen
      controller={controller}
      newCard={newCard}
      onOpenCard={(userId) => navigator.push({ name: 'playerCard', userId })}
      onBack={navigator.goBack}
    />
  );
}
