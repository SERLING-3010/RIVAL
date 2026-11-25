import { describe, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';

import type { SquadController } from '../src/controllers/useSquad';
import { SPECIAL_CODES } from '../src/domain/cardTiers';
import type { Squad } from '../src/domain/squadModels';
import { SquadScreen } from '../src/ui/screens/SquadScreen';
import { team } from './fixtures';

const squad: Squad = {
  team: team(1, 'Chuchuwaza'),
  media: 66,
  wins: 2,
  draws: 1,
  losses: 0,
  level: 1540,
  badges: ['Primera victoria'],
  players_per_side: 3,
  formation: '1-1',
  suggested: true,
  starters: [
    { user_id: 1, position: 'Arquero' },
    { user_id: 2, position: null },
    { user_id: 3, position: null },
  ],
  subs: [],
  members: [
    {
      user_id: 1,
      display_name: 'Ana Gil',
      position: 'Arquero',
      role: 'CAPTAIN',
      media: 70,
      tier: 'PLATA',
      matches: 12,
      goals: 7,
      wins: 8,
      rating_average: 7.4,
      hat_tricks: 1,
      badges: 3,
    },
    {
      user_id: 2,
      display_name: 'Luis Ruiz',
      position: null,
      role: 'PLAYER',
      media: 66,
      tier: 'BRONCE',
      matches: 4,
      goals: 1,
      wins: 2,
      rating_average: null,
      hat_tricks: 0,
      badges: 1,
    },
    {
      user_id: 3,
      display_name: 'Tú',
      position: null,
      role: 'COACH',
      media: 62,
      tier: 'BRONCE',
      matches: 0,
      goals: 0,
      wins: 0,
      rating_average: null,
      hat_tricks: 0,
      badges: 0,
    },
  ],
  card: {
    tier: 'PLATA',
    next_tier: 'ORO',
    media_to_next: 9,
    display_tier: 'RUBI',
    chosen: null,
    available: ['BASIC', 'RUBI'],
    goals: 9,
    clean_sheets: 1,
    cups: 0,
    leagues: 0,
    specials: SPECIAL_CODES.map((code) => ({
      code,
      min_media: 75,
      earned_at: code === 'RUBI' ? '2026-11-25T12:00:00Z' : null,
      goals: [{ label: '50 goles del equipo', current: 9, target: 50 }],
    })),
  },
  crest: null,
  can_edit: true,
};

const controller = (): SquadController => ({
  state: { kind: 'success', data: squad },
  handleReload: jest.fn(),
  compare: null,
  picked: [],
  handlePick: jest.fn(),
  action: { busy: false, message: null, run: jest.fn(async () => undefined) },
  handleChooseDesign: jest.fn(async () => undefined),
  handleSaveCrest: jest.fn(async () => undefined),
});

describe('SquadScreen', () => {
  test('muestra el equipo, la cancha sugerida y abre la ficha al tocar una carta', async () => {
    const open = jest.fn();
    await render(<SquadScreen controller={controller()} onOpenCard={open} onBack={jest.fn()} />);
    expect(screen.getByText('1-1 · récord 2-1-0 · nivel 1540')).toBeTruthy(); // la barra de siempre
    expect(screen.getByLabelText('Media 66, carta Rubí')).toBeTruthy(); // solo el cuadro de la media cambia
    expect(screen.queryByText('ÁLBUM DEL EQUIPO')).toBeNull();
    await fireEvent.press(screen.getByText('Chuchuwaza'));
    expect(screen.getByText('ÁLBUM DEL EQUIPO')).toBeTruthy();
    expect(screen.getByLabelText('Rubí: conseguida')).toBeTruthy();
    expect(screen.getByText(/Alineación sugerida por media/)).toBeTruthy();
    const ana = screen.getByLabelText('Ana Gil, media 70, capitán');
    await fireEvent.press(ana); // tocar voltea la carta ahí mismo
    expect(open).not.toHaveBeenCalled();
    expect(screen.getByLabelText('Ana Gil, media 70, capitán. Reverso')).toBeTruthy();
    expect(screen.getByText('ARQUERO')).toBeTruthy();
    await fireEvent(ana, 'longPress'); // mantener presionado abre la ficha
    expect(open).toHaveBeenCalledWith(1);
  });

  test('las pestañas Jugadores y Comparar', async () => {
    const c = controller();
    await render(<SquadScreen controller={c} onOpenCard={jest.fn()} onBack={jest.fn()} />);
    await fireEvent.press(screen.getByText('Jugadores (3)'));
    expect(screen.getAllByText('12 PJ').length).toBeGreaterThan(0); // frente y reverso
    await fireEvent.press(screen.getByText('Comparar'));
    await fireEvent.press(screen.getByText('66 Luis Ruiz'));
    expect(c.handlePick).toHaveBeenCalledWith(2);
  });

  test('el DT cambia el diseño de la media y arma el escudo manteniendo presionado', async () => {
    const c = controller();
    await render(<SquadScreen controller={c} onOpenCard={jest.fn()} onBack={jest.fn()} />);
    await fireEvent(screen.getByLabelText('Media 66, carta Rubí'), 'longPress');
    expect(screen.getByText('Diseño del equipo')).toBeTruthy();
    await fireEvent.press(screen.getByText('Básica: Plata'));
    expect(c.handleChooseDesign).toHaveBeenCalledWith('BASIC');
    await fireEvent(screen.getByLabelText('Escudo de Chuchuwaza'), 'longPress');
    await fireEvent.press(screen.getByText('Círculo'));
    await fireEvent.press(screen.getByText('Estrella'));
    await fireEvent.press(screen.getByText('Guardar escudo'));
    expect(c.handleSaveCrest).toHaveBeenCalledWith('CIRCULO|#0B6B3A|#FFFFFF|ESTRELLA');
  });
});
