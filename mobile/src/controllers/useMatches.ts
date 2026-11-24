// Búsquedas de partido del equipo, partidos disponibles para responder y ofertas recibidas.

import { useCallback, useState } from 'react';

import type { MatchRequest, Offer, SearchScope } from '../domain/matchModels';
import { matchApi } from '../services/matchApi';
import type { Action } from './useAction';
import { useAction } from './useAction';
import type { Loader } from './useLoader';
import { useLoader } from './useLoader';

export interface MyRequestsController extends Loader<MatchRequest[]> {
  action: Action;
  handleCancel: (requestId: number) => Promise<void>;
}

export function useMyMatchRequests(token: string, teamId: number): MyRequestsController {
  const action = useAction();
  const loader = useLoader(
    () => matchApi.mine(token, teamId),
    (items) => items.length === 0,
    'Tu equipo aún no ha publicado búsquedas de partido.',
    `mine|${teamId}`,
  );
  const { handleReload } = loader;
  const handleCancel = useCallback(
    (requestId: number) =>
      action.run(() => matchApi.cancel(token, requestId), 'Búsqueda cancelada.', handleReload),
    [action, handleReload, token],
  );
  return { ...loader, action, handleCancel };
}

export interface FeedController extends Loader<MatchRequest[]> {
  scope: SearchScope;
  handleScope: (scope: SearchScope) => void;
}

export function useMatchFeed(token: string, teamId: number): FeedController {
  const [scope, setScope] = useState<SearchScope>('CITY');
  const loader = useLoader(
    () => matchApi.feed(token, teamId, scope, 5),
    (items) => items.length === 0,
    'No hay búsquedas de partido abiertas para tu equipo en este alcance.',
    `feed|${teamId}|${scope}`,
  );
  return { ...loader, scope, handleScope: setScope };
}

export interface OffersController extends Loader<Offer[]> {
  action: Action;
  handleDecide: (offerId: number, decision: 'accept' | 'reject' | 'withdraw') => Promise<void>;
}

const DECISION_MESSAGE = {
  accept: '¡Rival confirmado! Revisen y firmen el contrato en "Partidos pactados".',
  reject: 'Oferta rechazada.',
  withdraw: 'Oferta retirada.',
} as const;

export function useOffers(token: string, requestId: number): OffersController {
  const action = useAction();
  const loader = useLoader(
    () => matchApi.offers(token, requestId),
    (items) => items.length === 0,
    'Todavía no hay ofertas. Los equipos cercanos verán tu búsqueda.',
    `offers|${requestId}`,
  );
  const { handleReload } = loader;
  const handleDecide = useCallback(
    (offerId: number, decision: 'accept' | 'reject' | 'withdraw') =>
      action.run(() => matchApi.decide(token, offerId, decision), DECISION_MESSAGE[decision], handleReload),
    [action, handleReload, token],
  );
  return { ...loader, action, handleDecide };
}
