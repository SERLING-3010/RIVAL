// Configuración común de las pruebas de componentes (jest-expo).
import { jest } from '@jest/globals';

jest.mock('react-native-safe-area-context', () => {
  const mock: { default: unknown } = jest.requireActual('react-native-safe-area-context/jest/mock');
  return mock.default;
});
