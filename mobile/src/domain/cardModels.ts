// Carta del jugador (Sprint 20): lámina metálica por nivel y datos reales; nunca se compra.

import type { PlayerCard } from './managerModels.ts';

export type CardTier = 'BRONCE' | 'PLATA' | 'ORO' | 'ELITE';
export type RecentResult = 'W' | 'D' | 'L';

export interface CardFace {
  media: number;
  tier: CardTier;
  next_tier: CardTier | null;
  matches_to_next: number;
  hat_tricks: number;
  recent: RecentResult[];
  badges: string[];
}

export const TIER_LABEL: Record<CardTier, string> = {
  BRONCE: 'Bronce',
  PLATA: 'Plata',
  ORO: 'Oro',
  ELITE: 'Élite',
};

/** Paradas del degradado metálico (claro, oscuro, brillo, oscuro, claro). */
export const TIER_FOIL: Record<CardTier, [string, string, string, string, string]> = {
  BRONCE: ['#F3CFA9', '#B07945', '#F0C493', '#8A5A35', '#D9A374'],
  PLATA: ['#FFFFFF', '#A9B3BA', '#F2F5F7', '#8C979E', '#DDE3E7'],
  ORO: ['#FFF3C4', '#C99A35', '#FBE7A1', '#A87A22', '#F1D27A'],
  ELITE: ['#E6FFF0', '#2BD46B', '#C9F5DA', '#179C4C', '#9BEBBE'],
};

export const RESULT_LABEL: Record<RecentResult, string> = { W: 'G', D: 'E', L: 'P' };

export function initials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  const letters = parts.length > 1 ? [parts[0]?.[0], parts[parts.length - 1]?.[0]] : [parts[0]?.[0]];
  return letters.filter(Boolean).join('').toUpperCase() || '?';
}

/** Las seis estadísticas del frente, en el orden de la carta (dos columnas). */
export function frontStats(p: PlayerCard): { value: string; label: string }[] {
  return [
    { value: String(p.matches), label: 'PJ' },
    { value: String(p.wins), label: 'VIC' },
    { value: String(p.goals), label: 'GOL' },
    { value: p.rating_average === null ? '–' : p.rating_average.toFixed(1).replace('.', ','), label: 'VAL' },
    { value: String(p.card.hat_tricks), label: 'TRI' },
    { value: String(p.card.badges.length), label: 'INS' },
  ];
}

/** "Faltan 6 partidos para Élite" o "Nivel máximo". */
export function nextTierText(c: CardFace): string {
  if (c.next_tier === null) return 'Nivel máximo: Élite';
  const one = c.matches_to_next === 1;
  return `${one ? 'Falta' : 'Faltan'} ${c.matches_to_next} ${one ? 'partido' : 'partidos'} para ${TIER_LABEL[c.next_tier]}`;
}

export function goalsPerMatch(p: PlayerCard): string {
  return p.matches === 0 ? '0' : (p.goals / p.matches).toFixed(2).replace('.', ',');
}
