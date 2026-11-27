// Composición del Sprint 11: bandeja de pendientes y a dónde lleva cada uno.

import { usePending } from '../controllers/usePending';
import type { Route } from '../controllers/useNavigator';
import type { PendingItem } from '../domain/pendingModels';
import { PendingScreen } from '../ui/screens/PendingScreen';
import type { MatchCtx } from './MatchFlow';

/** Ruta que resuelve el pendiente, o null si falta el id (no debería pasar). */
export function routeFor(item: PendingItem): Route | null {
  const id = item.target_id;
  switch (item.target) {
    case 'contract':
      return id === null ? null : { name: 'contract', contractId: id };
    case 'team':
      return id === null ? null : { name: 'team', teamId: id };
    case 'league':
      return id === null ? null : { name: 'league', leagueId: id };
    case 'venue':
      return id === null ? null : { name: 'venue', venueId: id, match: null };
    case 'transfers':
      return { name: 'transferOffers' };
    case 'referee':
      return { name: 'refereeMatches' };
    case 'loans':
      return { name: 'loans' };
    case 'feed': // te retaron: se responde con una oferta desde las búsquedas del equipo
      return id === null ? null : { name: 'matchFeed', teamId: id, isAdmin: true };
    case 'offers': // ofertas para tu búsqueda: el dueño de la búsqueda decide
      return id === null
        ? null
        : { name: 'offers', requestId: id, isRequestAdmin: true, myTeamIds: [], requestOpen: true };
  }
}

export function Pending({ token, navigator }: MatchCtx) {
  return (
    <PendingScreen
      controller={usePending(token)}
      onOpen={(item) => {
        const route = routeFor(item);
        if (route) navigator.push(route);
      }}
      onBack={navigator.goBack}
    />
  );
}
