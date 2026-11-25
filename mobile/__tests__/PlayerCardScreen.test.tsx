import { describe, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';

import { SPECIAL_CODES } from '../src/domain/cardTiers';
import type { PlayerCard } from '../src/domain/managerModels';
import { PlayerCardScreen } from '../src/ui/screens/PlayerCardScreen';
import { team } from './fixtures';

const card: PlayerCard = {
  user_id: 7,
  display_name: 'Andrés Mejía',
  position: 'Delantero',
  sports: ['FOOTBALL'],
  teams: [team(1, 'Chuchuwaza')],
  matches: 24,
  goals: 18,
  wins: 14,
  draws: 4,
  losses: 6,
  rating_average: 8.1,
  rating_votes: 19,
  card: {
    media: 77,
    tier: 'ORO',
    next_tier: 'ORO_BRILLANTE',
    media_to_next: 3,
    display_tier: 'RUBI',
    market_value: 1480,
    specials: SPECIAL_CODES.map((code) => ({
      code,
      min_media: 75,
      earned_at: code === 'RUBI' ? '2026-11-25T12:00:00Z' : null,
      goals: [
        {
          label: code === 'ESMERALDA' ? '3 tripletes' : 'hazaña',
          current: code === 'ESMERALDA' ? 1 : 0,
          target: 3,
        },
      ],
    })),
    hat_tricks: 2,
    check_ins: 5,
    recent: ['W', 'L'],
    badges: ['Goleador'],
  },
};

describe('PlayerCardScreen', () => {
  test('muestra la carta con datos reales y se voltea al tocarla', async () => {
    const onBadges = jest.fn();
    await render(
      <PlayerCardScreen
        controller={{ state: { kind: 'success', data: card }, handleReload: jest.fn() }}
        onReport={jest.fn()}
        onBadges={onBadges}
        onBack={jest.fn()}
      />,
    );
    expect(screen.getByText('77')).toBeTruthy();
    expect(screen.getByText('Faltan 3 de media para Oro brillante')).toBeTruthy();
    expect(screen.getByText('RUBÍ')).toBeTruthy(); // la carta se dibuja con su mejor especial
    expect(screen.getByText('· 3 tripletes: 1 / 3')).toBeTruthy();
    expect(screen.getByText('≈ 1.480 monedas')).toBeTruthy();
    expect(screen.getByText('1 de 15')).toBeTruthy();
    expect(screen.getByLabelText('Rubí: conseguida')).toBeTruthy();
    expect(screen.getByLabelText('Diamante: bloqueada')).toBeTruthy();
    const flip = screen.getByLabelText('Carta de Andrés Mejía, media 77. Toca para ver la ficha completa.');
    await fireEvent.press(flip);
    expect(screen.getByLabelText('Ficha completa. Toca para ver el frente de la carta.')).toBeTruthy();
    expect(screen.getByText('14-4-6')).toBeTruthy();
    await fireEvent.press(screen.getByText('Insignias'));
    expect(onBadges).toHaveBeenCalledWith(7, 'Andrés Mejía');
  });
});
