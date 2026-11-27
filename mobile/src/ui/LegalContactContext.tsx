// Sprint 29: datos del responsable del tratamiento, disponibles para la política y «Mi cuenta».

import { createContext, useContext } from 'react';

import type { LegalContact } from '../domain/legalContact';
import { EMPTY_CONTACT } from '../domain/legalContact';

export const LegalContactContext = createContext<LegalContact>(EMPTY_CONTACT);

export function useLegalContactInfo(): LegalContact {
  return useContext(LegalContactContext);
}
