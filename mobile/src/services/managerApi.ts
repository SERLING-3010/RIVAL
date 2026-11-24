import type { MarketItem, PlayerCard, TeamManager, TransferOffer } from '../domain/managerModels';
import { request } from './httpClient';

export type OfferDecision = 'owner-accept' | 'owner-reject' | 'player-accept' | 'player-reject' | 'withdraw';

export const managerApi = {
  team: (token: string, teamId: number) =>
    request<TeamManager>('GET', `/api/v1/teams/${teamId}/manager`, { token }),

  setListed: (token: string, teamId: number, userId: number, listed: boolean) =>
    request<TeamManager>('POST', `/api/v1/teams/${teamId}/transfer-list`, {
      token,
      body: { user_id: userId, listed },
    }),

  market: (token: string, sport: string, city: string) =>
    request<MarketItem[]>('GET', '/api/v1/market', { token, query: { sport, city } }),

  offer: (token: string, teamId: number, playerId: number, amount: number) =>
    request<TransferOffer>('POST', `/api/v1/teams/${teamId}/transfer-offers`, {
      token,
      body: { player_id: playerId, amount },
    }),

  decide: (token: string, offerId: number, decision: OfferDecision) =>
    request<TransferOffer>('POST', `/api/v1/transfer-offers/${offerId}/${decision}`, { token }),

  myOffers: (token: string) => request<TransferOffer[]>('GET', '/api/v1/me/transfer-offers', { token }),

  card: (token: string, userId: number) =>
    request<PlayerCard>('GET', `/api/v1/players/${userId}/card`, { token }),

  lineup: (token: string, contractId: number, players: { user_id: number; goals: number }[]) =>
    request<{ contract_id: number }>('POST', `/api/v1/contracts/${contractId}/lineup`, {
      token,
      body: { players },
    }),
};
