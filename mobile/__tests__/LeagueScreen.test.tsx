import { describe, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';
import { Alert } from 'react-native';

import type { LeagueController } from '../src/controllers/useLeagues';
import type { LeagueDetail } from '../src/domain/leagueModels';
import type { User } from '../src/domain/models';
import { LeagueScreen } from '../src/ui/screens/LeagueScreen';
import { idleAction, team } from './fixtures';

const user: User = {
  id: 1,
  email: 'org@r.test',
  display_name: 'José Peña',
  roles: ['COACH'],
  sports: ['FOOTBALL'],
  city: 'Barranquilla',
  neighborhood: 'El Prado',
  position: null,
};

function detail(overrides: Partial<LeagueDetail> = {}): LeagueDetail {
  return {
    league: {
      id: 4,
      name: 'Liga del Prado',
      sport_code: 'FOOTBALL',
      modality_code: 'F7',
      city: 'Barranquilla',
      season: '2026-2',
      team_count: 1,
      referee_count: 0,
    },
    description: 'Sábados en la tarde',
    my_role: null,
    transfer_window_start: null,
    transfer_window_end: null,
    staff: [{ user_id: 1, display_name: 'José Peña', role: 'ORGANIZER' }],
    teams: [{ id: 10, team: team(2, 'Bravos'), status: 'APPROVED' }],
    referees: [],
    pending_teams: [],
    pending_referees: [],
    my_team_requests: [],
    my_referee_request: null,
    champion: null,
    closed_at: null,
    ...overrides,
  };
}

function controller(data: LeagueDetail): LeagueController {
  return {
    state: { kind: 'success', data },
    handleReload: jest.fn(),
    action: idleAction(),
    handleRequestTeam: jest.fn(async () => undefined),
    handleJoinAsReferee: jest.fn(async () => undefined),
    handleDecide: jest.fn(async () => undefined),
    handleCloseSeason: jest.fn(async () => undefined),
  };
}

const windowCtl = {
  action: idleAction(),
  handleSave: jest.fn(async () => undefined),
  handleClear: jest.fn(async () => undefined),
};

const myTeam = { team: team(1, 'Águilas'), my_role: 'COACH' as const, is_admin: true, pending_requests: 0 };

describe('LeagueScreen', () => {
  test('el DT ve su equipo elegible y puede pedir inscripción', async () => {
    const c = controller(detail());
    await render(
      <LeagueScreen
        controller={c}
        user={user}
        myTeams={[myTeam]}
        onSeason={jest.fn()}
        onCup={jest.fn()}
        windowController={windowCtl}
        onBack={jest.fn()}
      />,
    );
    expect(screen.getByText('Bravos · El Prado')).toBeTruthy();
    await fireEvent.press(screen.getByText('Inscribir a Águilas'));
    expect(c.handleRequestTeam).toHaveBeenCalledWith(1);
    expect(screen.queryByText(/Solicitudes por revisar/)).toBeNull();
  });

  test('el organizador aprueba solicitudes pendientes', async () => {
    const c = controller(
      detail({
        my_role: 'ORGANIZER',
        pending_teams: [{ id: 11, team: team(3, 'Cóndores'), status: 'PENDING' }],
        pending_referees: [{ id: 21, user_id: 5, display_name: 'Ana Ruiz', status: 'PENDING' }],
      }),
    );
    await render(
      <LeagueScreen
        controller={c}
        user={user}
        myTeams={[]}
        onSeason={jest.fn()}
        onCup={jest.fn()}
        windowController={windowCtl}
        onBack={jest.fn()}
      />,
    );
    expect(screen.getByText('Solicitudes por revisar (2)')).toBeTruthy();
    await fireEvent.press(screen.getAllByText('Aprobar')[1]!);
    expect(c.handleDecide).toHaveBeenCalledWith('referee', 21, 'approve');
  });

  test('con solicitud aprobada, el equipo puede salir de la liga', async () => {
    const c = controller(
      detail({ my_team_requests: [{ id: 10, team: team(1, 'Águilas'), status: 'APPROVED' }] }),
    );
    await render(
      <LeagueScreen
        controller={c}
        user={user}
        myTeams={[myTeam]}
        onSeason={jest.fn()}
        onCup={jest.fn()}
        windowController={windowCtl}
        onBack={jest.fn()}
      />,
    );
    expect(screen.queryByText('Inscribir a Águilas')).toBeNull();
    await fireEvent.press(screen.getByText('Salir de la liga'));
    expect(c.handleDecide).toHaveBeenCalledWith('team', 10, 'withdraw');
  });

  test('el organizador cierra la temporada con confirmación y luego se ve el campeón', async () => {
    const alert = jest.spyOn(Alert, 'alert');
    const c = controller(detail({ my_role: 'ORGANIZER' }));
    const props = { user, myTeams: [], onSeason: jest.fn(), onCup: jest.fn(), windowController: windowCtl };
    const view = await render(<LeagueScreen controller={c} {...props} onBack={jest.fn()} />);
    await fireEvent.press(screen.getByText('Cerrar temporada'));
    expect(alert).toHaveBeenCalledWith('¿Cerrar la temporada?', expect.any(String), expect.any(Array));
    const closed = controller(detail({ champion: team(2, 'Bravos'), closed_at: '2026-11-25T12:00:00Z' }));
    await view.rerender(<LeagueScreen controller={closed} {...props} onBack={jest.fn()} />);
    expect(screen.getByText('🏆 Bravos')).toBeTruthy();
    expect(screen.queryByText('Cerrar temporada')).toBeNull();
  });
});
