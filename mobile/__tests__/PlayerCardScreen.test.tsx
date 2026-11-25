import { describe, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';

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
    media: 78,
    tier: 'ORO',
    next_tier: 'ELITE',
    matches_to_next: 6,
    hat_tricks: 2,
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
    expect(screen.getByText('78')).toBeTruthy();
    expect(screen.getByText('Faltan 6 partidos para Élite')).toBeTruthy();
    const flip = screen.getByLabelText('Carta de Andrés Mejía, media 78. Toca para ver la ficha completa.');
    await fireEvent.press(flip);
    expect(screen.getByLabelText('Ficha completa. Toca para ver el frente de la carta.')).toBeTruthy();
    expect(screen.getByText('14-4-6')).toBeTruthy();
    await fireEvent.press(screen.getByText('Insignias'));
    expect(onBadges).toHaveBeenCalledWith(7, 'Andrés Mejía');
  });
});
