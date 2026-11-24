// Validaciones locales: ayudan a corregir antes de enviar. El backend vuelve a validar todo.

import type { UserRole } from './models';

export const MIN_AGE_YEARS = 18;
export const MIN_PASSWORD_LENGTH = 10;

export interface RegistrationForm {
  role: UserRole;
  displayName: string;
  email: string;
  password: string;
  birthDate: string; // dd/mm/aaaa tal como lo escribe la persona
  sports: string[];
  city: string;
  neighborhood: string;
  position: string;
}

export type FieldErrors<K extends string> = Partial<Record<K, string>>;

const DATE_PATTERN = /^(\d{2})\/(\d{2})\/(\d{4})$/;

/** Convierte dd/mm/aaaa a aaaa-mm-dd. Devuelve null si la fecha no existe. */
export function parseBirthDate(text: string): string | null {
  const match = DATE_PATTERN.exec(text.trim());
  if (!match) {
    return null;
  }
  const [, dd, mm, yyyy] = match;
  const day = Number(dd);
  const month = Number(mm);
  const year = Number(yyyy);
  const date = new Date(Date.UTC(year, month - 1, day));
  const valid =
    date.getUTCFullYear() === year && date.getUTCMonth() === month - 1 && date.getUTCDate() === day;
  return valid ? `${yyyy}-${mm}-${dd}` : null;
}

/** Igual que el backend: un 29 de febrero cumple el 1 de marzo en años no bisiestos. */
export function isAdult(isoBirthDate: string, today: Date): boolean {
  const [year, month, day] = isoBirthDate.split('-').map(Number);
  if (year === undefined || month === undefined || day === undefined) {
    return false;
  }
  // Date.UTC desborda el 29/02 de un año no bisiesto al 01/03, que es la regla deseada.
  const comingOfAge = new Date(Date.UTC(year + MIN_AGE_YEARS, month - 1, day));
  const todayUtc = Date.UTC(today.getFullYear(), today.getMonth(), today.getDate());
  return todayUtc >= comingOfAge.getTime();
}

export function validateRegistration(
  form: RegistrationForm,
  today: Date,
): FieldErrors<keyof RegistrationForm> {
  const errors: FieldErrors<keyof RegistrationForm> = {};
  if (form.displayName.trim().length < 2) {
    errors.displayName = 'Escribe tu nombre (mínimo 2 letras).';
  }
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(form.email.trim())) {
    errors.email = 'Escribe un correo válido, por ejemplo nombre@correo.com.';
  }
  if (form.password.length < MIN_PASSWORD_LENGTH) {
    errors.password = `Usa al menos ${MIN_PASSWORD_LENGTH} caracteres. Una frase funciona bien.`;
  }
  const iso = parseBirthDate(form.birthDate);
  if (iso === null) {
    errors.birthDate = 'Escribe tu fecha como dd/mm/aaaa, por ejemplo 05/10/1998.';
  } else if (!isAdult(iso, today)) {
    errors.birthDate = 'Por ahora RIVAL es solo para mayores de 18 años.';
  }
  if (form.sports.length === 0) {
    errors.sports = 'Elige al menos un deporte.';
  }
  if (form.city.trim().length < 2) {
    errors.city = 'Escribe tu ciudad.';
  }
  if (form.neighborhood.trim().length < 2) {
    errors.neighborhood = 'Escribe tu barrio. Solo se muestra el barrio, nunca tu ubicación exacta.';
  }
  return errors;
}
