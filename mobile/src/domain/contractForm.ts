// Formulario de propuesta de cambio: texto editable ↔ condiciones del contrato.
// Valida lo mismo que el backend para avisar antes de enviar; el backend es la autoridad.

import type { ContractTerms, CostSplit } from './contractModels';
// Extensión explícita: las pruebas de reglas corren en Node sin empaquetador.
import { isoToLocalText, parseLocalDateTime } from './dateTime.ts';
import type { PlaceKind } from './matchModels';

export interface ContractForm {
  kickoff: string;
  duration: string;
  referee: ContractTerms['referee_mode'];
  place: PlaceKind;
  placeNote: string;
  hostKit: string;
  guestKit: string;
  substitutions: string; // vacío = ilimitados
  fieldCost: CostSplit;
  refereeCost: CostSplit;
  notice: string;
  foulCaller: string;
  extraRules: string;
  note: string;
}

export function formFromTerms(terms: ContractTerms): ContractForm {
  return {
    kickoff: isoToLocalText(terms.kickoff_at),
    duration: String(terms.duration_minutes),
    referee: terms.referee_mode,
    place: terms.place_kind,
    placeNote: terms.place_note ?? '',
    hostKit: terms.host_kit_color,
    guestKit: terms.guest_kit_color,
    substitutions: terms.substitutions === null ? '' : String(terms.substitutions),
    fieldCost: terms.field_cost_split,
    refereeCost: terms.referee_cost_split,
    notice: String(terms.cancellation_notice_hours),
    foulCaller: terms.foul_caller_note ?? '',
    extraRules: terms.extra_rules ?? '',
    note: '',
  };
}

const wholeNumber = (text: string): number | null => (/^\d{1,3}$/.test(text.trim()) ? Number(text) : null);
const optional = (text: string): string | null => text.trim() || null;

export type FormResult = { ok: true; terms: ContractTerms } | { ok: false; error: string };

export function termsFromForm(form: ContractForm, now: Date): FormResult {
  const kickoff = parseLocalDateTime(form.kickoff);
  if (!kickoff) return { ok: false, error: 'Escribe la hora como dd/mm/aaaa hh:mm.' };
  if (Date.parse(kickoff) <= now.getTime()) return { ok: false, error: 'La hora del partido ya pasó.' };
  const duration = wholeNumber(form.duration);
  if (duration === null || duration < 20 || duration > 240) {
    return { ok: false, error: 'La duración va de 20 a 240 minutos.' };
  }
  const subs = form.substitutions.trim() === '' ? null : wholeNumber(form.substitutions);
  if (form.substitutions.trim() !== '' && (subs === null || subs > 30)) {
    return { ok: false, error: 'Los cambios van de 0 a 30; deja vacío para ilimitados.' };
  }
  const notice = wholeNumber(form.notice);
  if (notice === null || notice > 72)
    return { ok: false, error: 'El aviso de cancelación va de 0 a 72 horas.' };
  const hostKit = form.hostKit.trim();
  const guestKit = form.guestKit.trim();
  if (!hostKit || !guestKit) return { ok: false, error: 'Indica el color de uniforme de cada equipo.' };
  if (hostKit.toLocaleLowerCase('es') === guestKit.toLocaleLowerCase('es')) {
    return { ok: false, error: 'Los uniformes deben ser de colores distintos.' };
  }
  return {
    ok: true,
    terms: {
      kickoff_at: kickoff,
      duration_minutes: duration,
      referee_mode: form.referee,
      place_kind: form.place,
      place_note: optional(form.placeNote),
      host_kit_color: hostKit,
      guest_kit_color: guestKit,
      substitutions: subs,
      field_cost_split: form.fieldCost,
      referee_cost_split: form.refereeCost,
      cancellation_notice_hours: notice,
      foul_caller_note: form.referee === 'WITHOUT' ? optional(form.foulCaller) : null,
      extra_rules: optional(form.extraRules),
    },
  };
}
