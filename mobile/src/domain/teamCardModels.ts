// Carta del equipo (Sprint 23): la lámina de la barra del equipo y sus especiales por hazañas del equipo.

import type { BaseTier, CardTier, SpecialCard } from './cardModels.ts';
import { nextSpecials } from './cardProgress.ts';

export interface TeamCard {
  tier: BaseTier; // básica por la media de los titulares
  next_tier: BaseTier | null;
  media_to_next: number;
  display_tier: CardTier; // la elegida, o su mejor especial, o la básica
  chosen: string | null; // elección guardada: código, "BASIC" o null (automático)
  available: string[]; // "BASIC" y las especiales ganadas
  goals: number;
  clean_sheets: number;
  cups: number;
  leagues: number;
  specials: SpecialCard[];
}

/** "15-3-6 · 61 goles · ◆ 2/15": lo esencial en una línea de la barra. */
export function teamFacts(record: [number, number, number], card: TeamCard | null): string {
  const parts = [record.join('-')];
  if (card) {
    parts.push(`${card.goals} ${card.goals === 1 ? 'gol' : 'goles'}`);
    parts.push(`◆ ${card.specials.filter((s) => s.earned_at !== null).length}/${card.specials.length}`);
  }
  return parts.join(' · ');
}

/** "Rubí · 10 victorias: 7/10" para la línea bajo la barra; null si ya tiene todas. */
export function nextTeamSpecialText(card: TeamCard, media: number): string | null {
  const [next] = nextSpecials({ media, specials: card.specials }, 1);
  if (!next) return null;
  const goals = next.goals.map((g) => `${g.label}: ${g.current}/${g.target}`).join(' · ');
  return `${next.label} · ${next.mediaOk ? '' : `media ${next.minMedia} · `}${goals}`;
}
