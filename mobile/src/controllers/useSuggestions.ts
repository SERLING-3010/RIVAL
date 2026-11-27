// Rivales sugeridos para un equipo, cada uno con por qué aparece.

import type { Suggestion } from '../domain/suggestionModels';
import { suggestionApi } from '../services/suggestionApi';
import type { Loader } from './useLoader';
import { useLoader } from './useLoader';

export function useSuggestions(token: string, teamId: number): Loader<Suggestion[]> {
  return useLoader(
    () => suggestionApi.rivals(token, teamId),
    (items) => items.length === 0,
    'Por ahora no hay sugerencias. Prueba "Buscar rival" para ver todos los equipos de tu ciudad.',
    `suggestions|${teamId}`,
  );
}
