import { describe, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';

import { ResultPanel } from '../src/ui/components/ResultPanel';
import { ActivityScreen } from '../src/ui/screens/ActivityScreen';
import { contract } from './fixtures';

describe('ResultPanel', () => {
  test('valida el marcador antes de reportar', async () => {
    const onReport = jest.fn();
    await render(<ResultPanel contract={contract()} canReport busy={false} onReport={onReport} />);
    await fireEvent.changeText(screen.getByLabelText('Goles de Águilas'), '3');
    await fireEvent.press(screen.getByText('Reportar marcador'));
    expect(onReport).not.toHaveBeenCalled();
    expect(screen.getByText(/números de 0 a 999/)).toBeTruthy();
    await fireEvent.changeText(screen.getByLabelText('Goles de Bravos'), '1');
    await fireEvent.press(screen.getByText('Reportar marcador'));
    expect(onReport).toHaveBeenCalledWith(3, 1);
  });

  test('muestra la disputa con lo que reportó cada equipo y sin formulario si no puede reportar', async () => {
    const result = {
      status: 'DISPUTED' as const,
      host_score: null,
      guest_score: null,
      reports: [
        { side: 'HOST' as const, host_score: 2, guest_score: 1, reported_at: '' },
        { side: 'GUEST' as const, host_score: 1, guest_score: 1, reported_at: '' },
      ],
    };
    await render(
      <ResultPanel contract={contract({ result })} canReport={false} busy={false} onReport={jest.fn()} />,
    );
    expect(screen.getByText('En disputa: los marcadores no coinciden')).toBeTruthy();
    expect(screen.getByText('Bravos reportó: Águilas 1 – 1 Bravos')).toBeTruthy();
    expect(screen.queryByText('Reportar marcador')).toBeNull();
  });

  test('confirmado muestra el marcador final', async () => {
    const result = { status: 'CONFIRMED' as const, host_score: 4, guest_score: 2, reports: [] };
    await render(
      <ResultPanel contract={contract({ result })} canReport={false} busy={false} onReport={jest.fn()} />,
    );
    expect(screen.getByText('Resultado: 4 – 2')).toBeTruthy();
  });
});

describe('ActivityScreen', () => {
  test('muestra quién hizo el cambio y el antes y después', async () => {
    const item = {
      occurred_at: '2026-11-23T15:00:00Z',
      action: 'CONTRACT_VERSION_PROPOSED',
      entity: 'match_contract',
      entity_id: '7',
      actor_type: 'HUMAN',
      actor_name: 'José Peña',
      approver_name: null,
      before: { host_kit_color: 'Oscuro' },
      after: { host_kit_color: 'Rojo', version: 2 },
    };
    await render(
      <ActivityScreen
        title="Actividad del partido"
        controller={{ state: { kind: 'success', data: [item] }, handleReload: jest.fn() }}
        onBack={jest.fn()}
      />,
    );
    expect(screen.getByText('Propuso cambios al contrato')).toBeTruthy();
    expect(screen.getByText(/José Peña/)).toBeTruthy();
    expect(screen.getByText('uniforme local: Oscuro → Rojo')).toBeTruthy();
  });
});
