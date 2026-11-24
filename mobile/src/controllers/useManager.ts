// Modo manager: vista del equipo (monedas, plantilla, ofertas), mercado, ficha y ofertas del jugador.

import { useCallback } from 'react';

import type { MarketItem, PlayerCard, TeamManager, TransferOffer } from '../domain/managerModels';
import { parseOffer } from '../domain/managerRules';
import type { OfferDecision } from '../services/managerApi';
import { managerApi } from '../services/managerApi';
import type { Action } from './useAction';
import { useAction } from './useAction';
import type { Loader } from './useLoader';
import { useLoader } from './useLoader';

const DECISION_MESSAGE: Record<OfferDecision, string> = {
  'owner-accept': 'Aceptaste. Ahora el jugador debe aceptar su traspaso.',
  'owner-reject': 'Oferta rechazada.',
  'player-accept': '¡Traspaso completado! Ya eres parte de tu nuevo equipo.',
  'player-reject': 'Rechazaste el traspaso. Sigues en tu equipo.',
  withdraw: 'Oferta retirada.',
};

export interface ManagerController extends Loader<TeamManager> {
  action: Action;
  handleListed: (userId: number, listed: boolean) => Promise<void>;
  handleDecide: (offerId: number, decision: OfferDecision) => Promise<void>;
}

export function useTeamManager(token: string, teamId: number): ManagerController {
  const action = useAction();
  const loader = useLoader(
    () => managerApi.team(token, teamId),
    () => false,
    '',
    `manager|${teamId}`,
  );
  const { handleReload } = loader;
  const handleListed = useCallback(
    (userId: number, listed: boolean) =>
      action.run(
        () => managerApi.setListed(token, teamId, userId, listed),
        listed ? 'Jugador en el mercado de fichajes.' : 'Jugador fuera del mercado.',
        handleReload,
      ),
    [action, handleReload, teamId, token],
  );
  const handleDecide = useCallback(
    (offerId: number, decision: OfferDecision) =>
      action.run(() => managerApi.decide(token, offerId, decision), DECISION_MESSAGE[decision], handleReload),
    [action, handleReload, token],
  );
  return { ...loader, action, handleListed, handleDecide };
}

export interface MarketController extends Loader<MarketItem[]> {
  action: Action;
  /** Devuelve el error de validación, o null si la oferta se envió (o falló en el servidor). */
  handleOffer: (playerId: number, amountText: string, balance: number) => Promise<string | null>;
}

export function useMarket(token: string, buyerTeamId: number, sport: string, city: string): MarketController {
  const action = useAction();
  const loader = useLoader(
    () => managerApi.market(token, sport, city),
    (items) => items.length === 0,
    'No hay jugadores transferibles de este deporte en tu ciudad.',
    `market|${sport}|${city}`,
  );
  const handleOffer = useCallback(
    async (playerId: number, amountText: string, balance: number) => {
      const parsed = parseOffer(amountText, balance);
      if (!parsed.ok) return parsed.error;
      await action.run(
        () => managerApi.offer(token, buyerTeamId, playerId, parsed.amount),
        'Oferta enviada. Primero decide su DT y después el jugador.',
      );
      return null;
    },
    [action, buyerTeamId, token],
  );
  return { ...loader, action, handleOffer };
}

export function usePlayerCard(token: string, userId: number): Loader<PlayerCard> {
  return useLoader(
    () => managerApi.card(token, userId),
    () => false,
    '',
    `card|${userId}`,
  );
}

export interface MyOffersController extends Loader<TransferOffer[]> {
  action: Action;
  handleDecide: (offerId: number, accept: boolean) => Promise<void>;
}

export function useMyTransferOffers(token: string): MyOffersController {
  const action = useAction();
  const loader = useLoader(
    () => managerApi.myOffers(token),
    (items) => items.length === 0,
    'No tienes ofertas de traspaso por responder.',
    'my-transfer-offers',
  );
  const { handleReload } = loader;
  const handleDecide = useCallback(
    (offerId: number, accept: boolean) => {
      const decision: OfferDecision = accept ? 'player-accept' : 'player-reject';
      return action.run(
        () => managerApi.decide(token, offerId, decision),
        DECISION_MESSAGE[decision],
        handleReload,
      );
    },
    [action, handleReload, token],
  );
  return { ...loader, action, handleDecide };
}
