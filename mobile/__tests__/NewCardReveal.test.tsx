import { describe, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';
import { Text } from 'react-native';

import { NewCardReveal } from '../src/ui/components/NewCardReveal';

describe('NewCardReveal', () => {
  test('sobre sellado: al tocar se revela la carta nueva y se cierra con ¡Vamos!', async () => {
    const done = jest.fn();
    await render(
      <NewCardReveal tier="RUBI" owner="tuya" onDone={done}>
        <Text>carta</Text>
      </NewCardReveal>,
    );
    expect(screen.getByText('¡SUBISTE DE CARTA!')).toBeTruthy();
    expect(screen.queryByText('carta')).toBeNull();
    await fireEvent.press(screen.getByLabelText('Revelar la carta nueva'));
    expect(screen.getByText(/NUEVA CARTA/)).toBeTruthy();
    expect(screen.getByText('carta')).toBeTruthy();
    expect(screen.getByText('RARA')).toBeTruthy();
    expect(screen.getByText('Es tuya para siempre, aunque la media baje.')).toBeTruthy();
    await fireEvent.press(screen.getByText('¡Vamos!'));
    expect(done).toHaveBeenCalled();
  });

  test('sin carta nueva no muestra nada', async () => {
    await render(
      <NewCardReveal tier={null} owner="tuya" onDone={jest.fn()}>
        <Text>carta</Text>
      </NewCardReveal>,
    );
    expect(screen.queryByText('¡SUBISTE DE CARTA!')).toBeNull();
  });
});
