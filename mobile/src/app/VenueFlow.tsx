// Composición del Sprint 6: mis establecimientos, registrar uno, detalle y reservar cancha para un partido.

import { useCreateVenue } from '../controllers/useCreateVenue';
import { useMyVenues, useVenue, useVenueSearch } from '../controllers/useVenues';
import type { MatchToBook } from '../domain/venueModels';
import { CreateVenueScreen } from '../ui/screens/CreateVenueScreen';
import { VenueScreen } from '../ui/screens/VenueScreen';
import { VenuesScreen } from '../ui/screens/VenuesScreen';
import type { MatchCtx } from './MatchFlow';

export function MyVenues({ token, navigator }: MatchCtx) {
  return (
    <VenuesScreen
      title="Mi establecimiento"
      lead="Registra tus canchas, publica franjas libres y confirma las reservas de los equipos."
      controller={useMyVenues(token)}
      onOpen={(venueId) => navigator.push({ name: 'venue', venueId, match: null })}
      onCreate={() => navigator.push({ name: 'createVenue' })}
      onBack={navigator.goBack}
    />
  );
}

export function CreateVenue({ token, navigator, user }: MatchCtx) {
  const controller = useCreateVenue(token, user, (venueId) => {
    navigator.goBack();
    navigator.push({ name: 'venue', venueId, match: null });
  });
  return <CreateVenueScreen controller={controller} onBack={navigator.goBack} />;
}

export function BookVenue({
  token,
  navigator,
  match,
  city,
}: MatchCtx & { match: MatchToBook; city: string }) {
  return (
    <VenuesScreen
      title="Reservar cancha"
      lead={`Establecimientos en ${city} con canchas para tu partido. Elige uno para ver sus franjas libres.`}
      controller={useVenueSearch(token, city, match.sportCode)}
      onOpen={(venueId) => navigator.push({ name: 'venue', venueId, match })}
      onBack={navigator.goBack}
    />
  );
}

export function VenueDetail({
  token,
  navigator,
  sports,
  venueId,
  match,
}: MatchCtx & { venueId: number; match: MatchToBook | null }) {
  return (
    <VenueScreen
      controller={useVenue(token, venueId)}
      sports={sports}
      match={match}
      onBooked={() => {
        navigator.goBack(); // sale del establecimiento
        navigator.goBack(); // y de la búsqueda: vuelve al contrato, que se recarga
      }}
      onBack={navigator.goBack}
    />
  );
}
