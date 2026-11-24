import { describe, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';

import type { ModerationController } from '../src/controllers/useModeration';
import type { ReportController } from '../src/controllers/useReport';
import { TrustCards } from '../src/ui/components/TrustCards';
import { ModerationScreen } from '../src/ui/screens/ModerationScreen';
import { ReportScreen } from '../src/ui/screens/ReportScreen';
import { idleAction } from './fixtures';

describe('ReportScreen', () => {
  test('elige el motivo y envía', async () => {
    const c: ReportController = {
      category: 'AGGRESSION',
      description: '',
      error: null,
      action: idleAction(),
      handleCategory: jest.fn(),
      handleDescription: jest.fn(),
      handleSubmit: jest.fn(async () => undefined),
    };
    await render(<ReportScreen controller={c} targetName="Bravos" onBack={jest.fn()} />);
    expect(screen.getByText('Reportar a Bravos')).toBeTruthy();
    await fireEvent.press(screen.getByText('No se presentó al partido'));
    expect(c.handleCategory).toHaveBeenCalledWith('NO_SHOW');
    await fireEvent.press(screen.getByText('Enviar reporte'));
    expect(c.handleSubmit).toHaveBeenCalled();
  });
});

describe('ModerationScreen', () => {
  test('decidir exige motivo y la suspensión, días válidos', async () => {
    const c: ModerationController = {
      state: {
        kind: 'success',
        data: {
          reports: [
            { id: 4, category: 'AGGRESSION', description: 'Insultos', target: 'Luis', created_at: '' },
          ],
          appeals: [],
        },
      },
      handleReload: jest.fn(),
      action: idleAction(),
      handleDismiss: jest.fn(async () => undefined),
      handleSanction: jest.fn(async () => undefined),
      handleAppealDecision: jest.fn(async () => undefined),
    };
    await render(<ModerationScreen controller={c} onBack={jest.fn()} />);
    await fireEvent.press(screen.getByText('Descartar'));
    expect(c.handleDismiss).not.toHaveBeenCalled();
    await fireEvent.changeText(screen.getByLabelText('Motivo de la decisión'), 'Agresión comprobada');
    await fireEvent.changeText(screen.getByLabelText('Días de suspensión (1 a 30)'), '45');
    await fireEvent.press(screen.getByText('Suspender'));
    expect(c.handleSanction).not.toHaveBeenCalled();
    await fireEvent.changeText(screen.getByLabelText('Días de suspensión (1 a 30)'), '3');
    await fireEvent.press(screen.getByText('Suspender'));
    expect(c.handleSanction).toHaveBeenCalledWith(4, 'SUSPENSION', 3, 'Agresión comprobada');
  });
});

describe('TrustCards', () => {
  test('avisa la suspensión vigente y muestra la cola al moderador', async () => {
    const ends = new Date(Date.now() + 86_400_000).toISOString();
    const me = {
      is_moderator: true,
      sanctions: [
        {
          id: 1,
          kind: 'SUSPENSION' as const,
          reason: 'x',
          ends_at: ends,
          status: 'ACTIVE' as const,
          created_at: new Date().toISOString(),
          appeal_text: null,
          appeal_outcome: null,
        },
      ],
    };
    await render(<TrustCards me={me} onMySanctions={jest.fn()} onModeration={jest.fn()} />);
    expect(screen.getByText('Tu cuenta está suspendida')).toBeTruthy();
    expect(screen.getByText('Moderación')).toBeTruthy();
  });
});
