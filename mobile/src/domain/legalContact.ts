// Datos del responsable del tratamiento (Sprint 29, Ley 1581). Llegan del servidor (`GET /api/v1/legal`):
// viven en su configuración y no en el código, que es público. Lo que falte se muestra «por definir».

import type { LegalSection } from './legalTerms.ts';

export interface LegalContact {
  name: string;
  address: string;
  email: string;
  phone: string;
  attends: string; // quién atiende las solicitudes
  hosting: string; // proveedor del servidor
  since: string; // desde cuándo rige la política
}

export const EMPTY_CONTACT: LegalContact = {
  name: '',
  address: '',
  email: '',
  phone: '',
  attends: '',
  hosting: '',
  since: '',
};

/** Reemplaza {name}, {email}… en los textos; lo vacío queda como «por definir». */
export function fillLegal(sections: LegalSection[], c: LegalContact): LegalSection[] {
  const value = (key: string) => (c[key as keyof LegalContact] || '').trim() || 'por definir';
  return sections.map((s) => ({ ...s, body: s.body.replace(/\{(\w+)\}/g, (_m, key: string) => value(key)) }));
}

/** Correo ya armado para ejercer los derechos; null si el servidor aún no tiene correo de privacidad. */
export function privacyMailto(c: LegalContact): string | null {
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(c.email.trim())) return null;
  const subject = encodeURIComponent('Solicitud sobre mis datos personales en RIVAL');
  const body = encodeURIComponent(
    'Hola. Quiero (marca una): conocer / corregir / suprimir mis datos / revocar la autorización.\n' +
      'Correo de mi cuenta en RIVAL:\nDetalle de mi solicitud:\n',
  );
  return `mailto:${c.email.trim()}?subject=${subject}&body=${body}`;
}
