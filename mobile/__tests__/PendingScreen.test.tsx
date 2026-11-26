import { describe, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';

import { routeFor } from '../src/app/PendingFlow';
import type { PendingItem } from '../src/domain/pendingModels';
import { PendingScreen } from '../src/ui/screens/PendingScreen';

const item = (overrides: Partial<PendingItem>): PendingItem => ({
  kind: 'SIGN_CONTRACT',
  title: 'Firmar: Águilas vs Bravos',
  detail: 'Falta la firma de tu equipo.',
  target: 'contract',
  target_id: 7,
  due_at: new Date(Date.now() + 3_600_000).toISOString(),
  ...overrides,
});

describe('PendingScreen', () => {
  test('muestra los pendientes, marca lo urgente y abre el elegido', async () => {
    const onOpen = jest.fn();
    const pending = [
      item({}),
      item({
        kind: 'TRANSFER_PLAYER',
        title: 'Oferta de traspaso por ti',
        target: 'transfers',
        target_id: 3,
        due_at: null,
      }),
    ];
    await render(
      <PendingScreen
        controller={{ state: { kind: 'success', data: pending }, handleReload: jest.fn() }}
        onOpen={onOpen}
        onBack={jest.fn()}
      />,
    );
    expect(screen.getByText('Urgente')).toBeTruthy();
    await fireEvent.press(screen.getByText('Oferta de traspaso por ti'));
    expect(onOpen).toHaveBeenCalledWith(pending[1]);
  });
});

describe('routeFor', () => {
  test('cada destino lleva a su pantalla', () => {
    expect(routeFor(item({}))).toEqual({ name: 'contract', contractId: 7 });
    expect(routeFor(item({ target: 'team', target_id: 2 }))).toEqual({ name: 'team', teamId: 2 });
    expect(routeFor(item({ target: 'league', target_id: 4 }))).toEqual({ name: 'league', leagueId: 4 });
    expect(routeFor(item({ target: 'venue', target_id: 5 }))).toEqual({
      name: 'venue',
      venueId: 5,
      match: null,
    });
    expect(routeFor(item({ target: 'transfers' }))).toEqual({ name: 'transferOffers' });
    expect(routeFor(item({ target: 'referee' }))).toEqual({ name: 'refereeMatches' });
    expect(routeFor(item({ target: 'feed', target_id: 3 }))).toEqual({
      name: 'matchFeed',
      teamId: 3,
      isAdmin: true,
    });
    expect(routeFor(item({ target: 'offers', target_id: 9 }))).toEqual({
      name: 'offers',
      requestId: 9,
      isRequestAdmin: true,
      myTeamIds: [],
      requestOpen: true,
    });
    expect(routeFor(item({ target_id: null }))).toBeNull();
  });
});
