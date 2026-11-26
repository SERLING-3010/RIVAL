// Sprint 29: lo que está prendido en este lanzamiento, disponible para cualquier pantalla.
// La raíz de la app lo carga una vez del backend; las pantallas solo lo leen.

import { createContext, useContext } from 'react';

import type { Features } from '../domain/features';
import { ALL_FEATURES } from '../domain/features';

export const FeaturesContext = createContext<Features>(ALL_FEATURES);

export function useFeatures(): Features {
  return useContext(FeaturesContext);
}
