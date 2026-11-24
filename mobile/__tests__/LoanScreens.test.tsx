import { describe, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';

import type { LoanRequestController, MyLoansController } from '../src/controllers/useLoans';
import type { TransferWindowController } from '../src/controllers/useTransferWindow';
import type { Loan } from '../src/domain/loanModels';
import { TransferWindowCard } from '../src/ui/components/TransferWindowCard';
import { LoanRequestScreen } from '../src/ui/screens/LoanRequestScreen';
import { LoansScreen } from '../src/ui/screens/LoansScreen';
import { idleAction, team } from './fixtures';

const loan = (id: number, status: Loan['status']): Loan => ({
  id,
  contract_id: 7,
  player_id: 30 + id,
  player_name: `Jugador ${id}`,
  from_team: 'Bravos',
  to_team: 'Águilas',
  status,
  kickoff_at: '2026-11-28T18:00:00-05:00',
});

describe('LoansScreen', () => {
  test('el DT dueño presta y el jugador acepta; cada uno con su decisión', async () => {
    const c: MyLoansController = {
      state: { kind: 'success', data: [loan(1, 'PENDING_OWNER'), loan(2, 'PENDING_PLAYER')] },
      handleReload: jest.fn(),
      action: idleAction(),
      handleDecide: jest.fn(async () => undefined),
    };
    await render(<LoansScreen controller={c} onBack={jest.fn()} />);
    await fireEvent.press(screen.getByText('Prestar al jugador'));
    expect(c.handleDecide).toHaveBeenCalledWith(1, 'owner-accept');
    await fireEvent.press(screen.getByText('Acepto jugar prestado'));
    expect(c.handleDecide).toHaveBeenCalledWith(2, 'player-accept');
    await fireEvent.press(screen.getAllByText('Rechazar')[1]!);
    expect(c.handleDecide).toHaveBeenCalledWith(2, 'player-reject');
  });
});

describe('LoanRequestScreen', () => {
  test('solo ofrece jugadores (no DT) del equipo elegido', async () => {
    const c: LoanRequestController = {
      current: { state: { kind: 'success', data: [] }, handleReload: jest.fn() },
      teams: { state: { kind: 'success', data: [] }, handleReload: jest.fn() },
      squad: {
        state: {
          kind: 'success',
          data: {
            team: team(2, 'Bravos'),
            admin_user_id: 20,
            members: [
              { user_id: 20, display_name: 'Profe', role: 'COACH', position: null },
              { user_id: 21, display_name: 'Luis', role: 'PLAYER', position: 'Arquero' },
            ],
          },
        },
        handleReload: jest.fn(),
      },
      selectedTeam: 2,
      action: idleAction(),
      handleSelectTeam: jest.fn(),
      handleRequest: jest.fn(async () => undefined),
    };
    await render(<LoanRequestScreen controller={c} onBack={jest.fn()} />);
    expect(screen.queryByText('Profe')).toBeNull();
    await fireEvent.press(screen.getByText('Pedir prestado'));
    expect(c.handleRequest).toHaveBeenCalledWith(21);
  });
});

describe('TransferWindowCard', () => {
  const ctl = () => ({
    action: idleAction(),
    handleSave: jest.fn<TransferWindowController['handleSave']>(async () => undefined),
    handleClear: jest.fn(async () => undefined),
  });

  test('el organizador guarda una ventana válida y ve el error si está invertida', async () => {
    const c = ctl();
    await render(<TransferWindowCard start={null} end={null} canEdit controller={c} />);
    expect(screen.getByText('Sin ventana: los traspasos están abiertos.')).toBeTruthy();
    await fireEvent.changeText(screen.getByLabelText('Abre (dd/mm/aaaa hh:mm)'), '15/12/2026 00:00');
    await fireEvent.changeText(screen.getByLabelText('Cierra (dd/mm/aaaa hh:mm)'), '01/12/2026 00:00');
    await fireEvent.press(screen.getByText('Guardar ventana'));
    expect(screen.getByText('El cierre debe ser después de la apertura.')).toBeTruthy();
    await fireEvent.changeText(screen.getByLabelText('Cierra (dd/mm/aaaa hh:mm)'), '20/12/2026 00:00');
    await fireEvent.press(screen.getByText('Guardar ventana'));
    expect(c.handleSave).toHaveBeenCalledWith('2026-12-15T00:00:00-05:00', '2026-12-20T00:00:00-05:00');
  });

  test('quien no organiza solo ve el estado de la ventana', async () => {
    await render(<TransferWindowCard start={null} end={null} canEdit={false} controller={ctl()} />);
    expect(screen.queryByText('Guardar ventana')).toBeNull();
  });
});
