// Sprint 29: datos del responsable del tratamiento. Se cargan una vez; sin red, quedan «por definir».

import { useEffect, useState } from 'react';

import type { LegalContact } from '../domain/legalContact';
import { EMPTY_CONTACT } from '../domain/legalContact';
import { legalApi } from '../services/legalApi';

export function useLegalContact(): LegalContact {
  const [contact, setContact] = useState<LegalContact>(EMPTY_CONTACT);
  useEffect(() => {
    let alive = true;
    void legalApi
      .get()
      .then((legal) => {
        if (alive) setContact({ ...EMPTY_CONTACT, ...legal.contact });
      })
      .catch(() => undefined);
    return () => {
      alive = false;
    };
  }, []);
  return contact;
}
