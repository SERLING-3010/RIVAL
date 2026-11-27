// Alineación táctica antes del partido (Sprint 19). Solo la ve el propio equipo.

export interface TacticSlot {
  user_id: number;
  display_name: string;
  position: string | null;
  still_going: boolean;
}

export interface Tactic {
  contract_id: number;
  team_id: number;
  players_per_side: number;
  uses_formation: boolean;
  suggested_formations: string[];
  formation: string | null;
  starters: TacticSlot[];
  subs: TacticSlot[];
  eligible: TacticSlot[];
  can_edit: boolean;
}

export type Role = 'starter' | 'sub' | 'out';

export interface TacticDraft {
  formation: string | null;
  roles: Record<number, Role>;
  positions: Record<number, string>;
}

/** Todos los jugadores que se pueden ubicar, en orden: titulares, suplentes y el resto. */
export function allPlayers(t: Tactic): TacticSlot[] {
  return [...t.starters, ...t.subs, ...t.eligible];
}

export function draftFrom(t: Tactic): TacticDraft {
  const roles: Record<number, Role> = {};
  const positions: Record<number, string> = {};
  for (const s of t.starters) {
    roles[s.user_id] = 'starter';
    positions[s.user_id] = s.position ?? '';
  }
  for (const s of t.subs) roles[s.user_id] = 'sub';
  for (const s of t.eligible) roles[s.user_id] = 'out';
  return { formation: t.formation, roles, positions };
}

/** Lo que impide guardar, o null si la alineación está completa. */
export function draftProblem(d: TacticDraft, t: Tactic): string | null {
  const starters = Object.keys(d.roles).filter((id) => d.roles[Number(id)] === 'starter');
  if (starters.length !== t.players_per_side) return `Elige exactamente ${t.players_per_side} titulares.`;
  if (starters.some((id) => (d.positions[Number(id)] ?? '').trim() === ''))
    return 'Escribe la posición de cada titular.';
  if (t.uses_formation && d.formation) {
    const parts = d.formation.split('-').map(Number);
    const sum = parts.reduce((a, b) => a + b, 0);
    if (parts.some((n) => !Number.isInteger(n) || n < 1) || sum !== t.players_per_side - 1)
      return `La formación debe sumar ${t.players_per_side - 1} jugadores de campo (sin el arquero).`;
  }
  return null;
}

/** Cuerpo para la API: titulares con posición, en el orden de la lista, y suplentes. */
export function draftBody(d: TacticDraft, t: Tactic) {
  const ordered = allPlayers(t).map((p) => p.user_id);
  return {
    formation: t.uses_formation ? d.formation : null,
    starters: ordered
      .filter((id) => d.roles[id] === 'starter')
      .map((id) => ({ user_id: id, position: (d.positions[id] ?? '').trim() })),
    subs: ordered.filter((id) => d.roles[id] === 'sub'),
  };
}
