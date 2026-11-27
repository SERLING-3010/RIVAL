import { describe, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';

import type { CheckInController } from '../src/controllers/useCheckIn';
import type { CheckInBoard } from '../src/domain/checkInModels';
import { VenueLocationCard } from '../src/ui/components/VenueLocationCard';
import { CheckInScreen } from '../src/ui/screens/CheckInScreen';
import { idleAction } from './fixtures';

const board = (over: Partial<CheckInBoard> = {}): CheckInBoard => ({
  contract_id: 7,
  unavailable: null,
  venue_name: 'Canchas El Prado',
  opens_at: '2026-11-28T17:00:00-05:00',
  closes_at: '2026-11-28T19:00:00-05:00',
  window_open: true,
  me_checked_in: false,
  items: [{ user_id: 2, display_name: 'Luis', checked_in_at: '2026-11-28T17:40:00-05:00' }],
  ...over,
});

const controller = (data: CheckInBoard): CheckInController => ({
  state: { kind: 'success', data },
  handleReload: jest.fn(),
  action: idleAction(),
  handleCheckIn: jest.fn(async () => undefined),
});

describe('CheckInScreen', () => {
  test('con la ventana abierta, "Llegué" hace el check-in y muestra quién llegó', async () => {
    const c = controller(board());
    await render(<CheckInScreen controller={c} onBack={jest.fn()} />);
    expect(screen.getByText('Llegaron (1)')).toBeTruthy();
    await fireEvent.press(screen.getByText('Llegué'));
    expect(c.handleCheckIn).toHaveBeenCalled();
  });

  test('sin cancha con ubicación no hay botón y se explica por qué', async () => {
    const reason = 'La cancha todavía no guardó su ubicación.';
    await render(
      <CheckInScreen controller={controller(board({ unavailable: reason }))} onBack={jest.fn()} />,
    );
    expect(screen.getByText(reason)).toBeTruthy();
    expect(screen.queryByText('Llegué')).toBeNull();
  });
});

describe('VenueLocationCard', () => {
  test('el dueño guarda la ubicación estando en la cancha', async () => {
    const c = { action: idleAction(), handleSaveHere: jest.fn(async () => undefined) };
    await render(<VenueLocationCard hasLocation={false} controller={c} />);
    await fireEvent.press(screen.getByText('Guardar: estoy en la cancha'));
    expect(c.handleSaveHere).toHaveBeenCalled();
  });
});
