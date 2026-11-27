// Plantilla del equipo en modo juego (Sprint 22): cartas, titulares sobre la cancha y comparación.

import type { CardFaceData, CardTier } from './cardModels.ts';
import { faceFromSquad } from './cardModels.ts';
import type { PlayerCard } from './managerModels.ts';
import type { TeamSummary } from './models.ts';
import type { TeamCard } from './teamCardModels.ts';

export interface SquadCard {
  user_id: number;
  display_name: string;
  position: string | null;
  role: 'COACH' | 'CAPTAIN' | 'PLAYER';
  media: number;
  tier: CardTier;
  matches: number;
  goals: number; // Sprint 22: las seis estadísticas de la carta, igual que en la ficha
  wins: number;
  rating_average: number | null;
  hat_tricks: number;
  badges: number;
}

export interface Starter {
  user_id: number;
  position: string | null;
}

export interface Squad {
  team: TeamSummary;
  media: number | null;
  wins: number;
  draws: number;
  losses: number;
  level: number | null;
  badges: string[];
  players_per_side: number;
  formation: string | null;
  suggested: boolean;
  starters: Starter[];
  subs: number[];
  members: SquadCard[];
  card: TeamCard | null; // Sprint 23: diseño del cuadro de la media; null sin titulares
  crest: string | null; // escudo armado; null = el predeterminado
  can_edit: boolean; // puede cambiar escudo y diseño (administrador)
}

export type SquadSort = 'media' | 'position' | 'matches';

export function roleMark(role: SquadCard['role']): string | null {
  return role === 'COACH' ? 'DT' : role === 'CAPTAIN' ? 'C' : null;
}

/** Filas de la cancha de arriba (ataque) hacia abajo (arquero). El primer titular es el arquero. */
export function pitchRows(formation: string | null, starters: Starter[]): Starter[][] {
  if (starters.length === 0) return [];
  const [keeper, ...field] = starters;
  const lines = (formation ?? '')
    .split('-')
    .map(Number)
    .filter((n) => Number.isInteger(n) && n > 0);
  if (lines.reduce((a, b) => a + b, 0) !== field.length) return [field, keeper ? [keeper] : []];
  const rows: Starter[][] = [];
  let next = 0;
  for (const size of lines) {
    rows.push(field.slice(next, next + size));
    next += size;
  }
  return [...rows.reverse(), keeper ? [keeper] : []];
}

const POSITION_ORDER = ['arq', 'por', 'def', 'lat', 'cen', 'vol', 'med', 'del', 'ext'];

function positionRank(position: string | null): number {
  const text = (position ?? '').toLowerCase();
  const found = POSITION_ORDER.findIndex((key) => text.startsWith(key));
  return found === -1 ? POSITION_ORDER.length : found;
}

export function sortMembers(members: SquadCard[], by: SquadSort): SquadCard[] {
  const copy = [...members];
  if (by === 'matches') return copy.sort((a, b) => b.matches - a.matches || b.media - a.media);
  if (by === 'position') return copy.sort((a, b) => positionRank(a.position) - positionRank(b.position));
  return copy.sort((a, b) => b.media - a.media);
}

export interface Axis {
  label: string;
  a: number;
  b: number;
  max: number;
  aText: string;
  bText: string;
}

/** Seis datos reales para comparar; el máximo de cada eje es el mayor de los dos (mínimo 1). */
export function compareAxes(a: PlayerCard, b: PlayerCard): Axis[] {
  const rating = (p: PlayerCard) => p.rating_average ?? 0;
  const fmt = (n: number) => (Number.isInteger(n) ? String(n) : n.toFixed(1).replace('.', ','));
  const rows: [string, number, number, number?][] = [
    ['Partidos', a.matches, b.matches],
    ['Goles', a.goals, b.goals],
    ['Victorias', a.wins, b.wins],
    ['Valoración', rating(a), rating(b), 10],
    ['Puntualidad', a.card.check_ins, b.card.check_ins],
    ['Insignias', a.card.badges.length, b.card.badges.length],
  ];
  return rows.map(([label, x, y, fixed]) => ({
    label,
    a: x,
    b: y,
    max: fixed ?? Math.max(1, x, y),
    aText: fmt(x),
    bText: fmt(y),
  }));
}

/** La misma carta de la ficha, con los datos de la plantilla. */
export function squadFace(c: SquadCard, teamName: string): CardFaceData {
  return faceFromSquad(
    {
      media: c.media,
      position: c.position,
      tier: c.tier,
      name: c.display_name,
      matches: c.matches,
      wins: c.wins,
      goals: c.goals,
      rating: c.rating_average,
      hatTricks: c.hat_tricks,
      badges: c.badges,
    },
    teamName,
  );
}
