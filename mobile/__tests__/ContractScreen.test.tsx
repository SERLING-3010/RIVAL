import { describe, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';
import { Alert } from 'react-native';

import { ContractScreen } from '../src/ui/screens/ContractScreen';
import { contract, contractController, version } from './fixtures';

const matchday = () => ({
  onChat: jest.fn(),
  onCheckIn: jest.fn(),
  onCallUp: jest.fn(),
  onRate: jest.fn(),
  onLoan: jest.fn(),
});

describe('ContractScreen', () => {
  test('el administrador que no ha firmado ve "Firmar" y la firma pide confirmación', async () => {
    const controller = contractController(contract());
    const alert = jest.spyOn(Alert, 'alert');
    await render(
      <ContractScreen
        controller={controller}
        onPropose={jest.fn()}
        onActivity={jest.fn()}
        onBookVenue={jest.fn()}
        onLineup={jest.fn()}
        matchday={matchday()}
        onBack={jest.fn()}
      />,
    );
    expect(screen.getByText(/Falta la firma de tu equipo/)).toBeTruthy();
    await fireEvent.press(screen.getByText('Firmar'));
    expect(alert).toHaveBeenCalledWith('¿Firmar esta versión?', expect.any(String), expect.any(Array));
  });

  test('un jugador que no administra no ve acciones', async () => {
    await render(
      <ContractScreen
        controller={contractController(contract({ is_admin: false }))}
        onPropose={jest.fn()}
        onActivity={jest.fn()}
        onBookVenue={jest.fn()}
        onLineup={jest.fn()}
        matchday={matchday()}
        onBack={jest.fn()}
      />,
    );
    expect(screen.queryByText('Firmar')).toBeNull();
    expect(screen.queryByText('Proponer cambios')).toBeNull();
    expect(screen.queryByText('Cancelar partido')).toBeNull();
  });

  test('con un cambio pendiente muestra la versión firmada vigente y permite rechazar', async () => {
    const signed = version(1, ['HOST', 'GUEST']);
    const pending = { ...version(2, ['GUEST']), terms: { ...signed.terms, duration_minutes: 90 } };
    const controller = contractController(
      contract({ signed, current: pending, versions: [signed, pending] }),
    );
    await render(
      <ContractScreen
        controller={controller}
        onPropose={jest.fn()}
        onActivity={jest.fn()}
        onBookVenue={jest.fn()}
        onLineup={jest.fn()}
        matchday={matchday()}
        onBack={jest.fn()}
      />,
    );
    expect(screen.getByText('Versión firmada vigente · v1')).toBeTruthy();
    expect(screen.getByText('Duración: 90 min')).toBeTruthy();
    await fireEvent.press(screen.getByText('Rechazar cambio'));
    expect(controller.handleRejectAmendment).toHaveBeenCalledWith(2);
  });

  test('cancelar exige un motivo de al menos 5 caracteres', async () => {
    const controller = contractController(contract());
    await render(
      <ContractScreen
        controller={controller}
        onPropose={jest.fn()}
        onActivity={jest.fn()}
        onBookVenue={jest.fn()}
        onLineup={jest.fn()}
        matchday={matchday()}
        onBack={jest.fn()}
      />,
    );
    await fireEvent.press(screen.getByText('Cancelar partido'));
    expect(controller.handleCancel).not.toHaveBeenCalled();
    await fireEvent.changeText(screen.getByLabelText('Motivo para cancelar'), 'Lluvia fuerte');
    await fireEvent.press(screen.getByText('Cancelar partido'));
    expect(controller.handleCancel).toHaveBeenCalledWith('Lluvia fuerte');
  });
});
