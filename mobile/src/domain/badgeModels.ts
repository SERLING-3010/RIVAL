// Logros e insignias (Sprint 17): se calculan de partidos, goles, check-ins y copas reales.

export interface Badge {
  code: string;
  name: string;
  description: string;
  earned_at: string | null;
  progress: string | null; // "3/10" mientras no se gana
}

export type BadgeOwner = 'player' | 'team';

/** Ganadas (la más reciente primero) y por ganar (en el orden del catálogo). */
export function splitBadges(badges: Badge[]): { earned: Badge[]; pending: Badge[] } {
  const earned = badges
    .filter((b) => b.earned_at !== null)
    .sort((a, b) => Date.parse(b.earned_at ?? '') - Date.parse(a.earned_at ?? ''));
  return { earned, pending: badges.filter((b) => b.earned_at === null) };
}
