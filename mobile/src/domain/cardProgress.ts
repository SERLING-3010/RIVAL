// Progreso de la carta (Sprint 23): barra hacia la siguiente básica, especiales en curso, álbum y valor.

import type { CardFace, SpecialCard } from './cardModels.ts';
import type { SpecialTier } from './cardTiers.ts';
import { TIERS } from './cardTiers.ts';

/** Avance de 0 a 1 en media entre la carta básica actual y la siguiente. */
export function tierProgress(c: CardFace): number {
  if (c.next_tier === null) return 1;
  const floor = TIERS[c.tier].media;
  const span = TIERS[c.next_tier].media - floor;
  return span <= 0 ? 1 : Math.min(1, Math.max(0, (c.media - floor) / span));
}

/** Qué tan cerca está de una especial, de 0 a 1: el promedio de sus hazañas y de su media. */
function closeness(s: SpecialCard, media: number): number {
  const parts = s.goals.map((g) => Math.min(1, g.current / g.target));
  parts.push(Math.min(1, media / s.min_media));
  return parts.reduce((a, b) => a + b, 0) / parts.length;
}

export interface SpecialInProgress {
  code: SpecialTier;
  label: string;
  mediaOk: boolean;
  minMedia: number;
  goals: SpecialCard['goals'];
}

/** Las especiales que aún no tiene, de la más cercana a la más lejana. */
export function nextSpecials(c: Pick<CardFace, 'media' | 'specials'>, count = 3): SpecialInProgress[] {
  return c.specials
    .filter((s) => s.earned_at === null)
    .map((s, order) => ({ s, order, score: closeness(s, c.media) }))
    .sort((a, b) => b.score - a.score || a.order - b.order)
    .slice(0, count)
    .map(({ s }) => ({
      code: s.code,
      label: TIERS[s.code].label,
      mediaOk: c.media >= s.min_media,
      minMedia: s.min_media,
      goals: s.goals,
    }));
}

export interface AlbumTile {
  tier: SpecialTier;
  label: string;
  swatch: string;
  owned: boolean;
}

/** Las quince casillas del álbum de especiales. */
export function albumTiles(specials: SpecialCard[]): AlbumTile[] {
  return specials.map((s) => ({
    tier: s.code,
    label: TIERS[s.code].label,
    swatch: TIERS[s.code].swatch,
    owned: s.earned_at !== null,
  }));
}

/** "480 monedas", con separador de miles. */
export function coinsText(value: number): string {
  return `${String(value).replace(/\B(?=(\d{3})+(?!\d))/g, '.')} monedas`;
}
