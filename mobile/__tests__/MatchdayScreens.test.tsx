import { describe, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';

import type { CallUpController, RatingsController } from '../src/controllers/useMatchday';
import type { SquadMember } from '../src/domain/managerModels';
import type { TeamCallUp } from '../src/domain/matchdayModels';
import { CallUpScreen } from '../src/ui/screens/CallUpScreen';
import { RateTeammatesScreen } from '../src/ui/screens/RateTeammatesScreen';
import { idleAction } from './fixtures';

const member = (id: number, name: string): SquadMember => ({
  user_id: id,
  display_name: name,
  role: 'PLAYER',
  position: null,
  listed: false,
  matches: 0,
  goals: 0,
});

function callup(data: TeamCallUp): CallUpController {
  return {
    state: { kind: 'success', data },
    handleReload: jest.fn(),
    action: idleAction(),
    handleSend: jest.fn(async () => undefined),
    handleRespond: jest.fn(async () => undefined),
  };
}

describe('CallUpScreen', () => {
  test('el convocado responde y el DT convoca a quien falta', async () => {
    const c = callup({
      contract_id: 7,
      items: [{ user_id: 1, display_name: 'José', status: 'INVITED' }],
      going: 0,
      not_going: 0,
      pending: 1,
    });
    const squad = [member(1, 'José'), member(2, 'Luis')];
    await render(<CallUpScreen controller={c} squad={squad} isAdmin myUserId={1} onBack={jest.fn()} />);
    expect(screen.getByText('Van 0 · No van 0 · Sin responder 1')).toBeTruthy();
    await fireEvent.press(screen.getByText('Voy'));
    expect(c.handleRespond).toHaveBeenCalledWith(true);
    await fireEvent.press(screen.getByText('Luis'));
    await fireEvent.press(screen.getByText('Enviar convocatoria'));
    expect(c.handleSend).toHaveBeenCalledWith([2]);
  });

  test('un jugador no convocado y sin administración no ve acciones', async () => {
    const c = callup({ contract_id: 7, items: [], going: 0, not_going: 0, pending: 0 });
    await render(
      <CallUpScreen
        controller={c}
        squad={[member(2, 'Luis')]}
        isAdmin={false}
        myUserId={2}
        onBack={jest.fn()}
      />,
    );
    expect(screen.queryByText('Voy')).toBeNull();
    expect(screen.queryByText('Enviar convocatoria')).toBeNull();
  });
});

describe('RateTeammatesScreen', () => {
  test('valida la nota antes de enviarla', async () => {
    const c: RatingsController = {
      state: { kind: 'success', data: [{ user_id: 3, display_name: 'Luis Díaz' }] },
      handleReload: jest.fn(),
      action: idleAction(),
      handleRate: jest.fn(async () => undefined),
    };
    await render(<RateTeammatesScreen controller={c} onBack={jest.fn()} />);
    await fireEvent.changeText(screen.getByLabelText('Nota para Luis Díaz (1 a 10)'), '11');
    await fireEvent.press(screen.getByText('Valorar'));
    expect(c.handleRate).not.toHaveBeenCalled();
    expect(screen.getByText('La valoración es un número del 1 al 10.')).toBeTruthy();
    await fireEvent.changeText(screen.getByLabelText('Nota para Luis Díaz (1 a 10)'), '8');
    await fireEvent.press(screen.getByText('Valorar'));
    expect(c.handleRate).toHaveBeenCalledWith(3, 8);
  });
});
