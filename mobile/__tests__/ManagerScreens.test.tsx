import { describe, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';
import { Alert } from 'react-native';

import type { ManagerController, MyOffersController } from '../src/controllers/useManager';
import type { TeamManager, TransferOffer } from '../src/domain/managerModels';
import { ManagerScreen } from '../src/ui/screens/ManagerScreen';
import { TransferOffersScreen } from '../src/ui/screens/TransferOffersScreen';
import { idleAction, team } from './fixtures';

const offer = (status: TransferOffer['status']): TransferOffer => ({
  id: 9,
  player_id: 3,
  player_name: 'Luis Díaz',
  from_team: team(1, 'Águilas'),
  to_team: team(2, 'Bravos'),
  amount: 300,
  status,
  created_at: '2026-11-24T15:00:00Z',
});

function manager(overrides: Partial<TeamManager> = {}): ManagerController {
  const data: TeamManager = {
    team: team(1, 'Águilas'),
    is_admin: true,
    balance: 1150,
    level: 1612,
    level_rd: 90,
    level_matches: 3,
    history: [{ amount: 150, reason: 'MATCH_REWARD', reference: 'contract:1', created_at: '' }],
    squad: [
      {
        user_id: 1,
        display_name: 'José',
        role: 'CAPTAIN',
        position: null,
        listed: false,
        matches: 1,
        goals: 0,
      },
      {
        user_id: 3,
        display_name: 'Luis Díaz',
        role: 'PLAYER',
        position: 'Extremo',
        listed: true,
        matches: 1,
        goals: 2,
      },
    ],
    offers_received: [offer('PENDING_OWNER')],
    offers_sent: [],
    ...overrides,
  };
  return {
    state: { kind: 'success', data },
    handleReload: jest.fn(),
    action: idleAction(),
    handleListed: jest.fn(async () => undefined),
    handleDecide: jest.fn(async () => undefined),
  };
}

describe('ManagerScreen', () => {
  test('el DT ve presupuesto, saca del mercado y acepta ofertas; el capitán no se lista', async () => {
    const c = manager();
    await render(
      <ManagerScreen controller={c} onOpenCard={jest.fn()} onMarket={jest.fn()} onBack={jest.fn()} />,
    );
    expect(screen.getByText('Presupuesto: 1.150 RC')).toBeTruthy();
    expect(screen.getAllByText(/del mercado|en el mercado/)).toHaveLength(1);
    await fireEvent.press(screen.getByText('Quitar del mercado'));
    expect(c.handleListed).toHaveBeenCalledWith(3, false);
    await fireEvent.press(screen.getByText('Aceptar oferta'));
    expect(c.handleDecide).toHaveBeenCalledWith(9, 'owner-accept');
  });

  test('un jugador sin administración no ve acciones', async () => {
    const c = manager({ is_admin: false, offers_received: [] });
    await render(
      <ManagerScreen controller={c} onOpenCard={jest.fn()} onMarket={jest.fn()} onBack={jest.fn()} />,
    );
    expect(screen.queryByText('Ir al mercado de fichajes')).toBeNull();
    expect(screen.queryByText('Quitar del mercado')).toBeNull();
  });
});

describe('TransferOffersScreen', () => {
  test('el jugador confirma antes de aceptar su traspaso', async () => {
    const c: MyOffersController = {
      state: { kind: 'success', data: [offer('PENDING_PLAYER')] },
      handleReload: jest.fn(),
      action: idleAction(),
      handleDecide: jest.fn(async () => undefined),
    };
    const alert = jest.spyOn(Alert, 'alert');
    await render(<TransferOffersScreen controller={c} onBack={jest.fn()} />);
    await fireEvent.press(screen.getByText('Aceptar traspaso'));
    expect(alert).toHaveBeenCalledWith('¿Pasar a Bravos?', expect.any(String), expect.any(Array));
    await fireEvent.press(screen.getByText('Rechazar'));
    expect(c.handleDecide).toHaveBeenCalledWith(9, false);
  });
});
