import { describe, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';

import type { Suggestion } from '../src/domain/suggestionModels';
import { SuggestionsScreen } from '../src/ui/screens/SuggestionsScreen';
import { team } from './fixtures';

const items: Suggestion[] = [
  {
    team: team(2, 'Bravos'),
    distance_band: 'UNDER_2_KM',
    level: 1510,
    reasons: ['Está a menos de 2 km', 'Su nivel es parecido al tuyo'],
  },
];

const controller = { state: { kind: 'success' as const, data: items }, handleReload: jest.fn() };

describe('SuggestionsScreen', () => {
  test('muestra los motivos y el administrador puede retar', async () => {
    const onChallenge = jest.fn();
    await render(
      <SuggestionsScreen controller={controller} canChallenge onChallenge={onChallenge} onBack={jest.fn()} />,
    );
    expect(screen.getByText('• Su nivel es parecido al tuyo')).toBeTruthy();
    await fireEvent.press(screen.getByText('Retar'));
    expect(onChallenge).toHaveBeenCalledWith(2);
  });

  test('quien no administra solo ve las sugerencias', async () => {
    await render(
      <SuggestionsScreen
        controller={controller}
        canChallenge={false}
        onChallenge={jest.fn()}
        onBack={jest.fn()}
      />,
    );
    expect(screen.queryByText('Retar')).toBeNull();
  });
});
