// Pendientes del usuario: se vuelven a pedir cada vez que se abre el inicio o la bandeja.

import type { PendingItem } from '../domain/pendingModels';
import { pendingApi } from '../services/pendingApi';
import type { Loader } from './useLoader';
import { useLoader } from './useLoader';

export function usePending(token: string): Loader<PendingItem[]> {
  return useLoader(
    () => pendingApi.mine(token),
    (items) => items.length === 0,
    'No tienes nada pendiente. ¡Todo al día!',
    'pending',
  );
}

/** Cuántos pendientes hay, o null mientras carga o si falló (el inicio no debe romperse por esto). */
export function pendingCount(loader: Loader<PendingItem[]>): number | null {
  if (loader.state.kind === 'success') return loader.state.data.length;
  if (loader.state.kind === 'empty') return 0;
  return null;
}
