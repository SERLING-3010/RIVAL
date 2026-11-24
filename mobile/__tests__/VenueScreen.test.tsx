import { describe, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';

import type { VenueController } from '../src/controllers/useVenues';
import type { Booking, Slot, VenueDetail } from '../src/domain/venueModels';
import { VenueScreen } from '../src/ui/screens/VenueScreen';
import { idleAction } from './fixtures';

const slot = (id: number, start: string, end: string): Slot => ({
  id,
  court_id: 1,
  court_name: 'Cancha 1',
  sport_code: 'FOOTBALL',
  starts_at: start,
  ends_at: end,
});

const booking: Booking = {
  id: 30,
  status: 'PENDING',
  contract_id: 7,
  venue_id: 2,
  venue_name: 'Canchas El Prado',
  address: 'Calle 72 # 45-10',
  slot: slot(1, '2026-12-01T23:00:00Z', '2026-12-02T01:00:00Z'),
  host_name: 'Águilas',
  guest_name: 'Bravos',
  requested_at: '2026-11-24T15:00:00Z',
};

function detail(overrides: Partial<VenueDetail> = {}): VenueDetail {
  return {
    venue: {
      id: 2,
      name: 'Canchas El Prado',
      address: 'Calle 72 # 45-10',
      city: 'Barranquilla',
      neighborhood: 'El Prado',
      reference_price: '80000.00',
      sports: ['FOOTBALL'],
    },
    is_owner: false,
    courts: [{ id: 1, name: 'Cancha 1', sport_code: 'FOOTBALL', surface: 'Sintética' }],
    slots: [
      slot(1, '2026-12-01T23:00:00Z', '2026-12-02T01:00:00Z'),
      slot(2, '2026-12-03T23:00:00Z', '2026-12-04T00:00:00Z'),
    ],
    pending_bookings: [],
    confirmed_bookings: [],
    ...overrides,
  };
}

function controller(data: VenueDetail): VenueController {
  return {
    state: { kind: 'success', data },
    handleReload: jest.fn(),
    action: idleAction(),
    handleAddCourt: jest.fn(async () => undefined),
    handleAddSlot: jest.fn(async () => null),
    handleDecide: jest.fn(async () => undefined),
    handleBook: jest.fn(async () => undefined),
  };
}

const sports = [{ code: 'FOOTBALL', name: 'Fútbol', modalities: [] }];

describe('VenueScreen', () => {
  test('para un partido muestra solo las franjas que lo cubren y permite reservar', async () => {
    const c = controller(detail());
    const match = {
      contractId: 7,
      kickoffAt: '2026-12-01T23:30:00Z',
      durationMinutes: 60,
      sportCode: 'FOOTBALL',
    };
    const onBooked = jest.fn();
    await render(
      <VenueScreen controller={c} sports={sports} match={match} onBooked={onBooked} onBack={jest.fn()} />,
    );
    expect(screen.getByText(/\$80\.000 por hora/)).toBeTruthy();
    expect(screen.getAllByText('Reservar esta franja')).toHaveLength(1);
    await fireEvent.press(screen.getByText('Reservar esta franja'));
    expect(c.handleBook).toHaveBeenCalledWith(7, 1, onBooked);
    expect(screen.queryByText('Agregar cancha')).toBeNull();
  });

  test('el dueño confirma reservas pendientes y ve sus herramientas', async () => {
    const c = controller(detail({ is_owner: true, pending_bookings: [booking] }));
    await render(
      <VenueScreen controller={c} sports={sports} match={null} onBooked={jest.fn()} onBack={jest.fn()} />,
    );
    expect(screen.getByText('Águilas vs Bravos')).toBeTruthy();
    await fireEvent.press(screen.getByText('Confirmar'));
    expect(c.handleDecide).toHaveBeenCalledWith(30, 'confirm');
    expect(screen.getByLabelText('Inicio (dd/mm/aaaa hh:mm)')).toBeTruthy();
  });
});
