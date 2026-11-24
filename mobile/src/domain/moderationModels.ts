// Moderación (Sprint 12): reportes, sanciones con apelación y bloqueos entre equipos.

import type { TeamSummary } from './models';

export type ReportCategory = 'AGGRESSION' | 'NO_SHOW' | 'FAKE_PROFILE' | 'OTHER';
export type SanctionKind = 'WARNING' | 'SUSPENSION';

export const CATEGORY_LABEL: Record<ReportCategory, string> = {
  AGGRESSION: 'Agresión o amenazas',
  NO_SHOW: 'No se presentó al partido',
  FAKE_PROFILE: 'Perfil falso',
  OTHER: 'Otro motivo',
};

export interface Sanction {
  id: number;
  kind: SanctionKind;
  reason: string;
  ends_at: string | null;
  status: 'ACTIVE' | 'REVOKED';
  created_at: string;
  appeal_text: string | null;
  appeal_outcome: 'UPHELD' | 'REVOKED' | null;
}

export interface ModerationMe {
  is_moderator: boolean;
  sanctions: Sanction[];
}

export interface ReportItem {
  id: number;
  category: ReportCategory;
  description: string;
  target: string;
  created_at: string;
}

export interface BlockedTeam {
  team: TeamSummary;
}

export type ReportTarget =
  { kind: 'user'; id: number; name: string } | { kind: 'team'; id: number; name: string };

/** Suspensión vigente (activa y sin vencer), si la hay. */
export function activeSuspension(me: ModerationMe, now: Date): Sanction | null {
  return (
    me.sanctions.find(
      (s) =>
        s.kind === 'SUSPENSION' &&
        s.status === 'ACTIVE' &&
        (s.ends_at === null || Date.parse(s.ends_at) > now.getTime()),
    ) ?? null
  );
}

/** Se puede apelar una sola vez, mientras la sanción siga activa y dentro de 14 días. */
export function canAppeal(s: Sanction, now: Date): boolean {
  const days = (now.getTime() - Date.parse(s.created_at)) / 86_400_000;
  return s.status === 'ACTIVE' && s.appeal_text === null && days <= 14;
}

export function textError(text: string, min: number, max: number, what: string): string | null {
  const length = text.trim().replace(/\s+/g, ' ').length;
  return length < min || length > max ? `${what} debe tener entre ${min} y ${max} caracteres.` : null;
}
