import { describe, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';

import type { ProposalController } from '../src/controllers/useContracts';
import type { OffersController } from '../src/controllers/useMatches';
import { formFromTerms } from '../src/domain/contractForm';
import type { Offer } from '../src/domain/matchModels';
import { OffersScreen } from '../src/ui/screens/OffersScreen';
import { ProposeContractScreen } from '../src/ui/screens/ProposeContractScreen';
import { idleAction, team, terms } from './fixtures';

function proposal(error: string | null = null): ProposalController {
  return {
    form: formFromTerms(terms),
    error,
    action: idleAction(),
    handleChange: jest.fn(),
    handleSubmit: jest.fn(async () => undefined),
  };
}

describe('ProposeContractScreen', () => {
  test('sin árbitro pregunta quién cobra las faltas y envía la propuesta', async () => {
    const controller = proposal();
    await render(
      <ProposeContractScreen
        controller={controller}
        hostName="Águilas"
        guestName="Bravos"
        onBack={jest.fn()}
      />,
    );
    expect(screen.getByText('¿Quién cobra las faltas dudosas? (opcional)')).toBeTruthy();
    expect(screen.queryByText('¿Quién paga el árbitro?')).toBeNull();
    await fireEvent.changeText(screen.getByLabelText('Uniforme de Bravos'), 'Blanco');
    expect(controller.handleChange).toHaveBeenCalledWith('guestKit', 'Blanco');
    await fireEvent.press(screen.getByText('Enviar y firmar propuesta'));
    expect(controller.handleSubmit).toHaveBeenCalled();
  });

  test('muestra el error de validación', async () => {
    await render(
      <ProposeContractScreen
        controller={proposal('Los uniformes deben ser de colores distintos.')}
        hostName="A"
        guestName="B"
        onBack={jest.fn()}
      />,
    );
    expect(screen.getByText('Los uniformes deben ser de colores distintos.')).toBeTruthy();
  });
});

const offer: Offer = {
  id: 5,
  request_id: 3,
  team: team(2, 'Bravos'),
  version: 1,
  proposed_start: '2026-11-28T23:00:00+00:00',
  referee_mode: 'WITHOUT',
  place_kind: 'INFORMAL',
  place_note: null,
  message: null,
  status: 'PENDING',
};

function offers(): OffersController {
  return {
    state: { kind: 'success', data: [offer] },
    handleReload: jest.fn(),
    action: idleAction(),
    handleDecide: jest.fn(async () => undefined),
  };
}

describe('OffersScreen (deuda del Sprint 2)', () => {
  test('el administrador que publicó puede aceptar o rechazar', async () => {
    const controller = offers();
    await render(
      <OffersScreen controller={controller} isRequestAdmin myTeamIds={[1]} requestOpen onBack={jest.fn()} />,
    );
    expect(screen.getByText('Aceptar')).toBeTruthy();
    await fireEvent.press(screen.getByText('Rechazar'));
    expect(controller.handleDecide).toHaveBeenCalledWith(5, 'reject');
  });

  test('el equipo que ofertó solo puede retirar su oferta', async () => {
    const controller = offers();
    await render(
      <OffersScreen
        controller={controller}
        isRequestAdmin={false}
        myTeamIds={[2]}
        requestOpen
        onBack={jest.fn()}
      />,
    );
    expect(screen.queryByText('Aceptar')).toBeNull();
    await fireEvent.press(screen.getByText('Retirar oferta'));
    expect(controller.handleDecide).toHaveBeenCalledWith(5, 'withdraw');
  });
});
