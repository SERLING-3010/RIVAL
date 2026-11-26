import { describe, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';
import { Alert } from 'react-native';

import type { MyDataController } from '../src/controllers/useMyData';
import { TERMS_VERSION } from '../src/domain/legalTerms';
import { LegalScreen } from '../src/ui/screens/LegalScreen';
import { MyDataScreen } from '../src/ui/screens/MyDataScreen';
import { TermsGateScreen } from '../src/ui/screens/TermsGateScreen';

const myData = (): MyDataController => ({
  action: { busy: false, message: null, run: jest.fn(async () => undefined) },
  password: 'clave',
  error: null,
  handlePassword: jest.fn(),
  handleExport: jest.fn(async () => undefined),
  handleDelete: jest.fn(async () => undefined),
});

describe('Términos y Mis datos (Sprint 27)', () => {
  test('quien ya tenía cuenta debe aceptar la versión vigente para seguir', async () => {
    const accept = jest.fn(async (_version: string) => undefined);
    await render(<TermsGateScreen onAccept={accept} onLogout={jest.fn()} />);
    await fireEvent.press(screen.getByText('Aceptar y seguir'));
    expect(screen.getByText('Marca la casilla para continuar.')).toBeTruthy();
    expect(accept).not.toHaveBeenCalled();
    await fireEvent.press(screen.getByRole('checkbox'));
    await fireEvent.press(screen.getByText('Aceptar y seguir'));
    expect(accept).toHaveBeenCalledWith(TERMS_VERSION);
  });

  test('los textos legales se pueden leer', async () => {
    await render(<LegalScreen doc="privacy" onBack={jest.fn()} />);
    expect(screen.getByText('Tus derechos')).toBeTruthy();
    expect(screen.getByText(/Nunca guardamos tu ubicación exacta/)).toBeTruthy();
  });

  test('descargar mis datos y eliminar la cuenta con confirmación', async () => {
    const c = myData();
    const alert = jest.spyOn(Alert, 'alert');
    await render(
      <MyDataScreen controller={c} onOpenLegal={jest.fn()} onBack={jest.fn()} onLogout={jest.fn()} />,
    );
    await fireEvent.press(screen.getAllByText('Descargar mis datos')[1]!); // [0] es el título de la tarjeta
    expect(c.handleExport).toHaveBeenCalled();
    await fireEvent.press(screen.getAllByText('Eliminar mi cuenta')[1]!);
    expect(alert).toHaveBeenCalledWith('¿Eliminar tu cuenta?', expect.any(String), expect.any(Array));
    expect(c.handleDelete).not.toHaveBeenCalled(); // solo después de confirmar
  });
});
