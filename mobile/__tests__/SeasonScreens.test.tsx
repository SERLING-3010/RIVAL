import { describe, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';

import type { RefereeMatchesController, SeasonController } from '../src/controllers/useSeason';
import type { RefereeMatch, Season } from '../src/domain/seasonModels';
import { RefereeMatchesScreen } from '../src/ui/screens/RefereeMatchesScreen';
import { SeasonScreen } from '../src/ui/screens/SeasonScreen';
import { idleAction, team } from './fixtures';

function season(data: Season): SeasonController {
  return {
    state: { kind: 'success', data },
    handleReload: jest.fn(),
    action: idleAction(),
    handleGenerate: jest.fn(async () => null),
    handleAssign: jest.fn(async () => undefined),
  };
}

const row = {
  team_id: 1,
  name: 'Águilas',
  played: 1,
  won: 1,
  drawn: 0,
  lost: 0,
  goals_for: 2,
  goals_against: 0,
  goal_difference: 2,
  points: 3,
};
const referees = [{ id: 4, user_id: 8, display_name: 'Ana Ruiz', status: 'APPROVED' as const }];

describe('SeasonScreen', () => {
  test('el organizador arma el calendario cuando no existe', async () => {
    const c = season({ calendar: [], table: [row] });
    await render(<SeasonScreen controller={c} canManage referees={referees} onBack={jest.fn()} />);
    expect(screen.getByText(/1\. Águilas · 1 · 1-0-0 · 2:0 · 3 pts/)).toBeTruthy();
    await fireEvent.changeText(screen.getByLabelText('Primera fecha (dd/mm/aaaa hh:mm)'), '05/12/2026 15:00');
    await fireEvent.press(screen.getByText('Generar calendario'));
    expect(c.handleGenerate).toHaveBeenCalledWith('05/12/2026 15:00', '7');
  });

  test('asigna un árbitro del cuerpo arbitral a un partido sin resultado', async () => {
    const fixture = {
      round: 1,
      contract_id: 30,
      host: team(1, 'Águilas'),
      guest: team(2, 'Bravos'),
      kickoff_at: '2026-12-05T20:00:00Z',
      status: 'NEGOTIATING' as const,
      result: null,
    };
    const c = season({ calendar: [fixture], table: [] });
    await render(<SeasonScreen controller={c} canManage referees={referees} onBack={jest.fn()} />);
    expect(screen.getByText('Fecha 1')).toBeTruthy();
    await fireEvent.press(screen.getByText('Ana Ruiz'));
    await fireEvent.press(screen.getByText('Asignar árbitro'));
    expect(c.handleAssign).toHaveBeenCalledWith(30, 8);
  });
});

describe('RefereeMatchesScreen', () => {
  test('el árbitro acepta y, después del partido, fija el resultado', async () => {
    const base: RefereeMatch = {
      assignment_id: 5,
      contract_id: 30,
      status: 'PENDING',
      league_name: 'Liga del Prado',
      host_name: 'Águilas',
      guest_name: 'Bravos',
      kickoff_at: '2020-01-01T20:00:00Z',
      place_kind: 'TO_AGREE',
      place_note: null,
      result_status: null,
      host_score: null,
      guest_score: null,
    };
    const c: RefereeMatchesController = {
      state: {
        kind: 'success',
        data: [base, { ...base, assignment_id: 6, contract_id: 31, status: 'ACCEPTED' }],
      },
      handleReload: jest.fn(),
      action: idleAction(),
      handleRespond: jest.fn(async () => undefined),
      handleReport: jest.fn(async () => undefined),
    };
    await render(<RefereeMatchesScreen controller={c} onChat={jest.fn()} onBack={jest.fn()} />);
    await fireEvent.press(screen.getByText('Aceptar partido'));
    expect(c.handleRespond).toHaveBeenCalledWith(5, true);
    await fireEvent.changeText(screen.getAllByLabelText('Goles de Águilas')[0]!, '2');
    await fireEvent.changeText(screen.getAllByLabelText('Goles de Bravos')[0]!, '1');
    await fireEvent.press(screen.getByText('Fijar resultado'));
    expect(c.handleReport).toHaveBeenCalledWith(31, 2, 1);
  });
});
