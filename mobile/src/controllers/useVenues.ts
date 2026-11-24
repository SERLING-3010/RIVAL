// Establecimientos: mis establecimientos, búsqueda para un partido y detalle con sus acciones.

import { useCallback } from 'react';

import type { VenueDetail, VenueSummary } from '../domain/venueModels';
import { slotFromForm } from '../domain/venueRules';
import { venueApi } from '../services/venueApi';
import type { Action } from './useAction';
import { useAction } from './useAction';
import type { Loader } from './useLoader';
import { useLoader } from './useLoader';

export function useMyVenues(token: string): Loader<VenueSummary[]> {
  return useLoader(
    () => venueApi.mine(token),
    (items) => items.length === 0,
    'Aún no registras tu establecimiento.',
    'my-venues',
  );
}

export function useVenueSearch(token: string, city: string, sport: string): Loader<VenueSummary[]> {
  return useLoader(
    () => venueApi.search(token, city, sport).then((page) => page.items),
    (items) => items.length === 0,
    `No hay establecimientos en ${city} con canchas de este deporte.`,
    `venues|${city}|${sport}`,
  );
}

export interface VenueController extends Loader<VenueDetail> {
  action: Action;
  handleAddCourt: (name: string, sportCode: string, surface: string) => Promise<void>;
  /** Devuelve un mensaje de error si el formulario no es válido; si es válido, publica la franja. */
  handleAddSlot: (courtId: number, startText: string, minutesText: string) => Promise<string | null>;
  handleDecide: (bookingId: number, decision: 'confirm' | 'reject') => Promise<void>;
  handleBook: (contractId: number, slotId: number, onDone: () => void) => Promise<void>;
}

export function useVenue(token: string, venueId: number): VenueController {
  const action = useAction();
  const loader = useLoader(
    () => venueApi.get(token, venueId),
    () => false,
    '',
    `venue|${venueId}`,
  );
  const { handleReload } = loader;
  const handleAddCourt = useCallback(
    (name: string, sportCode: string, surface: string) =>
      action.run(
        () => venueApi.addCourt(token, venueId, name.trim(), sportCode, surface.trim() || null),
        'Cancha agregada.',
        handleReload,
      ),
    [action, handleReload, token, venueId],
  );
  const handleAddSlot = useCallback(
    async (courtId: number, startText: string, minutesText: string) => {
      const slot = slotFromForm(startText, minutesText, new Date());
      if (!slot.ok) return slot.error;
      await action.run(
        () => venueApi.addSlot(token, courtId, slot.startsAt, slot.endsAt),
        'Franja publicada.',
        handleReload,
      );
      return null;
    },
    [action, handleReload, token],
  );
  const handleDecide = useCallback(
    (bookingId: number, decision: 'confirm' | 'reject') =>
      action.run(
        () => venueApi.decide(token, bookingId, decision),
        decision === 'confirm' ? 'Reserva confirmada.' : 'Reserva rechazada.',
        handleReload,
      ),
    [action, handleReload, token],
  );
  const handleBook = useCallback(
    (contractId: number, slotId: number, onDone: () => void) =>
      action.run(
        () => venueApi.book(token, contractId, slotId),
        'Reserva enviada. El establecimiento debe confirmarla.',
        onDone,
      ),
    [action, token],
  );
  return { ...loader, action, handleAddCourt, handleAddSlot, handleDecide, handleBook };
}
