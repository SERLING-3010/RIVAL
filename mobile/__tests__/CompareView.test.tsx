import { describe, expect, test } from '@jest/globals';
import { render, screen } from '@testing-library/react-native';

import type { PlayerCard } from '../src/domain/managerModels';
import { CompareView } from '../src/ui/components/CompareView';

const player = (id: number, name: string, matches: number): PlayerCard => ({
  user_id: id,
  display_name: name,
  position: null,
  sports: [],
  teams: [],
  matches,
  goals: 2,
  wins: 1,
  draws: 0,
  losses: 0,
  rating_average: 7,
  rating_votes: 3,
  card: {
    media: 60 + matches,
    tier: 'BRONCE',
    next_tier: 'PLATA',
    display_tier: 'BRONCE',
    specials: [],
    media_to_next: 0,
    market_value: 480,
    hat_tricks: 0,
    check_ins: 1,
    recent: [],
    badges: [],
  },
});

describe('CompareView', () => {
  test('dibuja el hexágono y las barras de los dos jugadores', async () => {
    await render(<CompareView pair={[player(1, 'Ana', 4), player(2, 'Luis', 2)]} />);
    expect(screen.getByLabelText('Hexágono de comparación en seis datos')).toBeTruthy();
    expect(screen.getAllByText('Puntualidad').length).toBeGreaterThan(0);
    expect(screen.getByText('4')).toBeTruthy();
  });
});
