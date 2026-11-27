import type { LegalContact } from '../domain/legalContact';
import { request } from './httpClient';

// Sprint 29: versión de los textos y datos del responsable, desde la configuración del servidor.
export const legalApi = {
  get: () => request<{ version: string; contact: LegalContact }>('GET', '/api/v1/legal'),
};
