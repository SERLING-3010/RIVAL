// Cartas nuevas (Sprint 23): qué especiales ganadas aún no se le han mostrado a quien mira.
// Se recuerda en el teléfono, por persona y por dueño de la carta (jugador o equipo).

import type { SpecialCard, SpecialTier } from './cardModels.ts';

export type CardOwner = 'player' | 'team';

/** Clave del almacenamiento seguro (solo letras, números y puntos). */
export function seenKey(owner: CardOwner, ownerId: number, viewerId: number): string {
  return `rival.seen.${owner}.${viewerId}.${ownerId}`;
}

/** Las especiales ganadas que todavía no se han revelado, en orden de dificultad. */
export function unseenSpecials(specials: SpecialCard[], seen: string[]): SpecialTier[] {
  return specials.filter((s) => s.earned_at !== null && !seen.includes(s.code)).map((s) => s.code);
}

/** Se revela solo la más difícil; las demás nuevas quedan vistas a la vez. */
export function toReveal(specials: SpecialCard[], seen: string[]): SpecialTier | null {
  const fresh = unseenSpecials(specials, seen);
  return fresh[fresh.length - 1] ?? null;
}

export function markSeen(specials: SpecialCard[], seen: string[]): string[] {
  return [...new Set([...seen, ...unseenSpecials(specials, seen)])];
}

/** Firma corta de lo ganado, para recalcular solo cuando cambia. */
export function earnedSignature(specials: SpecialCard[] | null): string {
  return (specials ?? [])
    .filter((s) => s.earned_at !== null)
    .map((s) => s.code)
    .join(',');
}
