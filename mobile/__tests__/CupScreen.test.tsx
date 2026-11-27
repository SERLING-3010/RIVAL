import { describe, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';

import type { CupController } from '../src/controllers/useCup';
import type { Cup } from '../src/domain/cupModels';
import type { ViewState } from '../src/domain/viewState';
import { CupScreen } from '../src/ui/screens/CupScreen';
import { idleAction } from './fixtures';

const cup: Cup = {
  league_id: 4,
  champion_name: null,
  can_manage: true,
  rounds: [
    {
      number: 1,
      name: 'Semifinal',
      planned_at: '2026-12-05T18:00:00-05:00',
      matches: [
        {
          id: 1,
          position: 0,
          host_team_id: 1,
          guest_team_id: null,
          host_name: 'Águilas',
          guest_name: null,
          contract_id: null,
          host_score: null,
          guest_score: null,
          winner_name: 'Águilas',
          needs_tiebreak: false,
        },
        {
          id: 2,
          position: 1,
          host_team_id: 2,
          guest_team_id: 3,
          host_name: 'Bravos',
          guest_name: 'Cóndores',
          contract_id: 9,
          host_score: 1,
          guest_score: 1,
          winner_name: null,
          needs_tiebreak: true,
        },
      ],
    },
  ],
};

const controller = (state: ViewState<Cup>): CupController => ({
  state,
  handleReload: jest.fn(),
  action: idleAction(),
  handleCreate: jest.fn(async () => null),
  handleTiebreak: jest.fn(async () => undefined),
});

describe('CupScreen', () => {
  test('muestra el cuadro, abre el partido y el organizador define penales', async () => {
    const c = controller({ kind: 'success', data: cup });
    const open = jest.fn();
    await render(<CupScreen controller={c} canManage onOpenContract={open} onBack={jest.fn()} />);
    expect(screen.getByText('Águilas (pasa directo)')).toBeTruthy();
    await fireEvent.press(screen.getByText('Bravos 1 – 1 Cóndores'));
    expect(open).toHaveBeenCalledWith(9);
    await fireEvent.press(screen.getByText('Ganó por penales: Cóndores'));
    expect(c.handleTiebreak).toHaveBeenCalledWith(2, 3);
    expect(screen.queryByText('Armar copa')).toBeNull();
  });

  test('sin copa, el organizador la arma', async () => {
    const c = controller({ kind: 'error', message: 'Esta liga todavía no tiene copa.', correlationId: null });
    await render(<CupScreen controller={c} canManage onOpenContract={jest.fn()} onBack={jest.fn()} />);
    await fireEvent.changeText(screen.getByLabelText('Primera ronda (dd/mm/aaaa hh:mm)'), '05/12/2026 18:00');
    await fireEvent.press(screen.getByText('Armar copa'));
    expect(c.handleCreate).toHaveBeenCalledWith('05/12/2026 18:00', '7');
  });
});
