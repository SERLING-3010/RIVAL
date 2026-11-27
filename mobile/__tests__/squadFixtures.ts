// Datos de prueba de la plantilla en modo juego (Sprints 22 y 23).
import { jest } from '@jest/globals';

import type { SquadController } from '../src/controllers/useSquad';
import { SPECIAL_CODES } from '../src/domain/cardTiers';
import type { Squad } from '../src/domain/squadModels';
import { team } from './fixtures';

export const squad: Squad = {
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

export const controller = (): SquadController => ({
  state: { kind: 'success', data: squad },
  handleReload: jest.fn(),
  compare: null,
  picked: [],
  handlePick: jest.fn(),
  action: { busy: false, message: null, run: jest.fn(async () => undefined) },
  handleChooseDesign: jest.fn(async () => undefined),
  handleSaveCrest: jest.fn(async () => undefined),
});
