import { describe, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';

import { SquadScreen } from '../src/ui/screens/SquadScreen';
import { controller } from './squadFixtures';

describe('SquadScreen', () => {
  test('muestra el equipo, la cancha sugerida y abre la ficha al tocar una carta', async () => {
    const open = jest.fn();
    await render(
      <SquadScreen
        controller={controller()}
        onOpenCard={open}
        onBack={jest.fn()}
        newCard={{ reveal: null, handleDone: jest.fn() }}
      />,
    );
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
    await render(
      <SquadScreen
        controller={c}
        onOpenCard={jest.fn()}
        onBack={jest.fn()}
        newCard={{ reveal: null, handleDone: jest.fn() }}
      />,
    );
    await fireEvent.press(screen.getByText('Jugadores (3)'));
    expect(screen.getAllByText('12 PJ').length).toBeGreaterThan(0); // frente y reverso
    await fireEvent.press(screen.getByText('Comparar'));
    await fireEvent.press(screen.getByText('66 Luis Ruiz'));
    expect(c.handlePick).toHaveBeenCalledWith(2);
  });

  test('el DT cambia el diseño de la media y arma el escudo manteniendo presionado', async () => {
    const c = controller();
    await render(
      <SquadScreen
        controller={c}
        onOpenCard={jest.fn()}
        onBack={jest.fn()}
        newCard={{ reveal: null, handleDone: jest.fn() }}
      />,
    );
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
