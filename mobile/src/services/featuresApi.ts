import type { Features } from '../domain/features';
import { request } from './httpClient';

// Sprint 29: qué está prendido en este lanzamiento. No requiere sesión.
export const featuresApi = {
  get: () => request<Features>('GET', '/api/v1/features'),
};
