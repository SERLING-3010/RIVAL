// Fechas y horas en hora de Colombia (UTC-5, sin horario de verano).
// Se escriben como dd/mm/aaaa hh:mm y viajan a la API en ISO 8601 con zona: ...-05:00.

const COLOMBIA_OFFSET_MINUTES = -5 * 60;
const PATTERN = /^(\d{2})\/(\d{2})\/(\d{4})\s+(\d{1,2}):(\d{2})$/;
const DAYS = ['dom', 'lun', 'mar', 'mié', 'jue', 'vie', 'sáb'];

const pad = (n: number) => String(n).padStart(2, '0');

/** "28/11/2026 18:30" → "2026-11-28T18:30:00-05:00", o null si la fecha u hora no existen. */
export function parseLocalDateTime(text: string): string | null {
  const match = PATTERN.exec(text.trim());
  if (!match) return null;
  const [, dd, mm, yyyy, hh, min] = match;
  const day = Number(dd);
  const month = Number(mm);
  const year = Number(yyyy);
  const hour = Number(hh);
  const minute = Number(min);
  const probe = new Date(Date.UTC(year, month - 1, day));
  const validDate =
    probe.getUTCFullYear() === year && probe.getUTCMonth() === month - 1 && probe.getUTCDate() === day;
  if (!validDate || hour > 23 || minute > 59) return null;
  return `${yyyy}-${mm}-${dd}T${pad(hour)}:${min}:00-05:00`;
}

/** Fecha ISO (cualquier zona) → "sáb 28/11 18:30" en hora de Colombia. */
export function formatLocal(iso: string): string {
  const instant = Date.parse(iso);
  if (Number.isNaN(instant)) return iso;
  const local = new Date(instant + COLOMBIA_OFFSET_MINUTES * 60_000);
  const day = DAYS[local.getUTCDay()] ?? '';
  return `${day} ${pad(local.getUTCDate())}/${pad(local.getUTCMonth() + 1)} ${pad(local.getUTCHours())}:${pad(local.getUTCMinutes())}`;
}

/** Texto dd/mm/aaaa hh:mm para dentro de `days` días a la hora indicada (hora de Colombia). */
export function localTextInDays(now: Date, days: number, hour: number): string {
  const local = new Date(now.getTime() + COLOMBIA_OFFSET_MINUTES * 60_000 + days * 86_400_000);
  return `${pad(local.getUTCDate())}/${pad(local.getUTCMonth() + 1)}/${local.getUTCFullYear()} ${pad(hour)}:00`;
}

/** Fecha ISO → texto editable dd/mm/aaaa hh:mm en hora de Colombia. */
export function isoToLocalText(iso: string): string {
  const local = new Date(Date.parse(iso) + COLOMBIA_OFFSET_MINUTES * 60_000);
  return `${pad(local.getUTCDate())}/${pad(local.getUTCMonth() + 1)}/${local.getUTCFullYear()} ${pad(local.getUTCHours())}:${pad(local.getUTCMinutes())}`;
}
