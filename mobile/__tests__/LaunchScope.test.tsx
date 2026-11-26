import { describe, expect, jest, test } from '@jest/globals';
import { render, screen } from '@testing-library/react-native';

import { FeaturesContext } from '../src/ui/FeaturesContext';
import { RolePickerScreen } from '../src/ui/screens/RolePickerScreen';

const launch = { sports: ['FOOTBALL'], referees: false, venues: false };

describe('Lanzamiento solo con fútbol (Sprint 29)', () => {
  test('al registrarse solo se ofrece jugador o DT', async () => {
    await render(
      <FeaturesContext.Provider value={launch}>
        <RolePickerScreen onPickRole={jest.fn()} onLogin={jest.fn()} />
      </FeaturesContext.Provider>,
    );
    expect(screen.getByText('Jugador')).toBeTruthy();
    expect(screen.getByText('Director técnico')).toBeTruthy();
    expect(screen.queryByText('Árbitro')).toBeNull();
    expect(screen.queryByText('Establecimiento deportivo')).toBeNull();
  });
});
