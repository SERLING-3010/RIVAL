import { describe, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';

import type { GoalClaimsController } from '../src/controllers/useGoalClaims';
import type { GoalClaim } from '../src/domain/goalKinds';
import { GoalClaimsPanel } from '../src/ui/components/GoalClaimsPanel';
import { GoalKindPicker } from '../src/ui/components/GoalKindPicker';

const claim = (over: Partial<GoalClaim> = {}): GoalClaim => ({
  id: 4,
  team_id: 1,
  user_id: 7,
  display_name: 'Andrés Mejía',
  kind: 'CHILENA',
  status: 'PENDING',
  claimed_at: '2026-11-25T12:00:00Z',
  can_decide: true,
  ...over,
});

const controller = (claims: GoalClaim[]): GoalClaimsController => ({
  state: { kind: 'success', data: claims },
  handleReload: jest.fn(),
  action: { busy: false, message: null, run: jest.fn(async () => undefined) },
  handleDecide: jest.fn(async () => undefined),
});

describe('GoalClaimsPanel', () => {
  test('el rival confirma o rechaza cada gol con tipo', async () => {
    const c = controller([
      claim(),
      claim({ id: 5, kind: 'OLIMPICO', status: 'CONFIRMED', can_decide: false }),
    ]);
    await render(<GoalClaimsPanel controller={c} />);
    expect(screen.getByText('Confirmado por el rival')).toBeTruthy();
    expect(screen.getAllByText('Confirmar')).toHaveLength(1); // solo el pendiente
    await fireEvent.press(screen.getByText('Confirmar'));
    expect(c.handleDecide).toHaveBeenCalledWith(4, true);
    await fireEvent.press(screen.getByText('No fue así'));
    expect(c.handleDecide).toHaveBeenCalledWith(4, false);
  });

  test('sin goles con tipo no se muestra', async () => {
    await render(
      <GoalClaimsPanel controller={{ ...controller([]), state: { kind: 'empty', message: '' } }} />,
    );
    expect(screen.queryByText('Goles especiales')).toBeNull();
  });
});

describe('GoalKindPicker', () => {
  test('suma tipos hasta los goles del jugador y deja quitarlos', async () => {
    const onAdd = jest.fn();
    const onRemove = jest.fn();
    await render(
      <GoalKindPicker name="Andrés" goals={2} marked={['CHILENA']} onAdd={onAdd} onRemove={onRemove} />,
    );
    await fireEvent.press(screen.getByLabelText('Sumar un gol de tipo Olímpico a Andrés'));
    expect(onAdd).toHaveBeenCalledWith('OLIMPICO');
    await fireEvent.press(screen.getByLabelText('Quitar Chilena de Andrés'));
    expect(onRemove).toHaveBeenCalledWith(0);
  });

  test('sin goles no aparece', async () => {
    await render(
      <GoalKindPicker name="Andrés" goals={0} marked={[]} onAdd={jest.fn()} onRemove={jest.fn()} />,
    );
    expect(screen.queryByText(/gol especial/)).toBeNull();
  });
});
