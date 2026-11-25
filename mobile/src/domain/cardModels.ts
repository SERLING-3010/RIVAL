// Carta del jugador (Sprints 20 y 23): lámina por nivel y datos reales; nunca se compra.

import type { PlayerCard } from './managerModels.ts';

import type { BaseTier, CardTier, SpecialTier } from './cardTiers.ts';
import { TIER_LABEL } from './cardTiers.ts';

export type { BaseTier, CardTier, SpecialTier } from './cardTiers.ts';
export { TIER_LABEL } from './cardTiers.ts';
export type RecentResult = 'W' | 'D' | 'L';

export interface FeatGoal {
  label: string; // "10 goles", "Gol de chilena"…
  current: number;
  target: number;
}

/** Una carta especial (Sprint 23): media mínima + hazañas; earned_at no es null si ya la ganó. */
export interface SpecialCard {
  code: SpecialTier;
  min_media: number;
  earned_at: string | null;
  goals: FeatGoal[];
}

export interface CardFace {
  media: number;
  tier: BaseTier; // carta básica, sale de la media
  next_tier: BaseTier | null;
  media_to_next: number;
  display_tier: CardTier; // la que se dibuja: su mejor especial o su básica
  market_value: number; // monedas RIVAL virtuales
  specials: SpecialCard[];
  hat_tricks: number;
  check_ins: number; // Sprint 22
  recent: RecentResult[];
  badges: string[];
}

export const RESULT_LABEL: Record<RecentResult, string> = { W: 'G', D: 'E', L: 'P' };

export function initials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  const letters = parts.length > 1 ? [parts[0]?.[0], parts[parts.length - 1]?.[0]] : [parts[0]?.[0]];
  return letters.filter(Boolean).join('').toUpperCase() || '?';
}

export interface Stat {
  value: string;
  label: string;
}

/** Lo que dibuja el frente de la carta; igual en la ficha y en la plantilla (Sprint 22). */
export interface CardFaceData {
  media: number;
  position: string;
  crest: string;
  tier: CardTier;
  name: string;
  stats: Stat[];
}

interface StatSource {
  matches: number;
  wins: number;
  goals: number;
  rating: number | null;
  hatTricks: number;
  badges: number;
}

function sixStats(s: StatSource): Stat[] {
  return [
    { value: String(s.matches), label: 'PJ' },
    { value: String(s.wins), label: 'VIC' },
    { value: String(s.goals), label: 'GOL' },
    { value: s.rating === null ? '–' : s.rating.toFixed(1).replace('.', ','), label: 'VAL' },
    { value: String(s.hatTricks), label: 'TRI' },
    { value: String(s.badges), label: 'INS' },
  ];
}

/** Las seis estadísticas del frente, en el orden de la carta (dos columnas). */
export function frontStats(p: PlayerCard): Stat[] {
  return sixStats({
    matches: p.matches,
    wins: p.wins,
    goals: p.goals,
    rating: p.rating_average,
    hatTricks: p.card.hat_tricks,
    badges: p.card.badges.length,
  });
}

const shortPosition = (position: string | null) => (position ?? '—').slice(0, 3).toUpperCase();

export function faceFromPlayer(p: PlayerCard): CardFaceData {
  const team = p.teams[0];
  return {
    media: p.card.media,
    position: shortPosition(p.position),
    crest: team ? initials(team.name) : '—',
    tier: p.card.display_tier,
    name: p.display_name,
    stats: frontStats(p),
  };
}

export interface SquadStatSource extends StatSource {
  media: number;
  position: string | null;
  tier: CardTier;
  name: string;
}

export function faceFromSquad(c: SquadStatSource, teamName: string): CardFaceData {
  return {
    media: c.media,
    position: shortPosition(c.position),
    crest: initials(teamName),
    tier: c.tier,
    name: c.name,
    stats: sixStats(c),
  };
}

/** "Faltan 4 de media para Oro común" o "Carta básica máxima: Oro brillante". */
export function nextTierText(c: CardFace): string {
  if (c.next_tier === null) return `Carta básica máxima: ${TIER_LABEL[c.tier]}`;
  const verb = c.media_to_next === 1 ? 'Falta' : 'Faltan';
  return `${verb} ${c.media_to_next} de media para ${TIER_LABEL[c.next_tier]}`;
}

export function goalsPerMatch(p: PlayerCard): string {
  return p.matches === 0 ? '0' : (p.goals / p.matches).toFixed(2).replace('.', ',');
}
