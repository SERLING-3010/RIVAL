import { describe, expect, jest, test } from '@jest/globals';
import { render, screen } from '@testing-library/react-native';

import type { Badge } from '../src/domain/badgeModels';
import { BadgesScreen } from '../src/ui/screens/BadgesScreen';

const badges: Badge[] = [
  {
    code: 'DEBUT',
    name: 'Debut',
    description: 'Jugó su primer partido.',
    earned_at: '2026-11-21T23:00:00Z',
    progress: null,
  },
  { code: 'GOALS_10', name: 'Goleador', description: 'Marcó 10 goles.', earned_at: null, progress: '3/10' },
];

describe('BadgesScreen', () => {
  test('separa las ganadas (con fecha) de las que faltan (con avance)', async () => {
    const controller = { state: { kind: 'success' as const, data: badges }, handleReload: jest.fn() };
    await render(<BadgesScreen title="Insignias de Ana" controller={controller} onBack={jest.fn()} />);
    expect(screen.getByText('Ganadas (1)')).toBeTruthy();
    expect(screen.getByText('sáb 21/11 18:00')).toBeTruthy();
    expect(screen.getByText('Por ganar (1)')).toBeTruthy();
    expect(screen.getByText('3/10')).toBeTruthy();
  });
});
