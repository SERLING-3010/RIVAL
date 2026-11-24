import type {
  BlockedTeam,
  ModerationMe,
  ReportCategory,
  ReportItem,
  Sanction,
  SanctionKind,
} from '../domain/moderationModels';
import { request } from './httpClient';

export interface ReportPayload {
  category: ReportCategory;
  description: string;
  target_user_id: number | null;
  target_team_id: number | null;
}

export const moderationApi = {
  report: (token: string, payload: ReportPayload) =>
    request<{ id: number }>('POST', '/api/v1/reports', { token, body: payload }),

  me: (token: string) => request<ModerationMe>('GET', '/api/v1/moderation/me', { token }),

  appeal: (token: string, sanctionId: number, text: string) =>
    request<ModerationMe>('POST', `/api/v1/sanctions/${sanctionId}/appeal`, { token, body: { text } }),

  queue: (token: string) => request<ReportItem[]>('GET', '/api/v1/moderation/reports', { token }),

  dismiss: (token: string, reportId: number, note: string) =>
    request<ReportItem[]>('POST', `/api/v1/moderation/reports/${reportId}/dismiss`, {
      token,
      body: { note },
    }),

  sanction: (token: string, reportId: number, kind: SanctionKind, days: number | null, reason: string) =>
    request<ReportItem[]>('POST', `/api/v1/moderation/reports/${reportId}/sanction`, {
      token,
      body: { kind, days, reason },
    }),

  appeals: (token: string) => request<Sanction[]>('GET', '/api/v1/moderation/appeals', { token }),

  decideAppeal: (token: string, sanctionId: number, revoke: boolean) =>
    request<Sanction[]>('POST', `/api/v1/moderation/appeals/${sanctionId}/decide`, {
      token,
      body: { revoke },
    }),

  blocks: (token: string, teamId: number) =>
    request<BlockedTeam[]>('GET', `/api/v1/teams/${teamId}/blocks`, { token }),

  block: (token: string, teamId: number, otherId: number) =>
    request<BlockedTeam[]>('POST', `/api/v1/teams/${teamId}/blocks`, { token, body: { team_id: otherId } }),

  unblock: (token: string, teamId: number, otherId: number) =>
    request<BlockedTeam[]>('POST', `/api/v1/teams/${teamId}/blocks/${otherId}/remove`, { token }),
};
