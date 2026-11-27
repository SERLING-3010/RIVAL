// Moderación: mis sanciones y apelación, cola del moderador y equipos bloqueados.

import { useCallback } from 'react';

import type {
  BlockedTeam,
  ModerationMe,
  ReportItem,
  Sanction,
  SanctionKind,
} from '../domain/moderationModels';
import { moderationApi } from '../services/moderationApi';
import type { Action } from './useAction';
import { useAction } from './useAction';
import type { Loader } from './useLoader';
import { useLoader } from './useLoader';

export interface MySanctionsController extends Loader<ModerationMe> {
  action: Action;
  handleAppeal: (sanctionId: number, text: string) => Promise<void>;
}

export function useModerationMe(token: string): MySanctionsController {
  const action = useAction();
  const loader = useLoader(
    () => moderationApi.me(token),
    () => false,
    '',
    'moderation-me',
  );
  const { handleReload } = loader;
  const handleAppeal = useCallback(
    (sanctionId: number, text: string) =>
      action.run(
        () => moderationApi.appeal(token, sanctionId, text),
        'Apelación enviada. La revisará otra persona moderadora.',
        handleReload,
      ),
    [action, handleReload, token],
  );
  return { ...loader, action, handleAppeal };
}

export interface ModerationQueue {
  reports: ReportItem[];
  appeals: Sanction[];
}

export interface ModerationController extends Loader<ModerationQueue> {
  action: Action;
  handleDismiss: (reportId: number, note: string) => Promise<void>;
  handleSanction: (
    reportId: number,
    kind: SanctionKind,
    days: number | null,
    reason: string,
  ) => Promise<void>;
  handleAppealDecision: (sanctionId: number, revoke: boolean) => Promise<void>;
}

export function useModerationQueue(token: string): ModerationController {
  const action = useAction();
  const loader = useLoader(
    async () => {
      const [reports, appeals] = await Promise.all([
        moderationApi.queue(token),
        moderationApi.appeals(token),
      ]);
      return { reports, appeals };
    },
    (q) => q.reports.length === 0 && q.appeals.length === 0,
    'No hay reportes ni apelaciones por revisar.',
    'moderation-queue',
  );
  const { handleReload } = loader;
  const handleDismiss = useCallback(
    (reportId: number, note: string) =>
      action.run(() => moderationApi.dismiss(token, reportId, note), 'Reporte descartado.', handleReload),
    [action, handleReload, token],
  );
  const handleSanction = useCallback(
    (reportId: number, kind: SanctionKind, days: number | null, reason: string) =>
      action.run(
        () => moderationApi.sanction(token, reportId, kind, days, reason),
        'Sanción aplicada.',
        handleReload,
      ),
    [action, handleReload, token],
  );
  const handleAppealDecision = useCallback(
    (sanctionId: number, revoke: boolean) =>
      action.run(
        () => moderationApi.decideAppeal(token, sanctionId, revoke),
        revoke ? 'Sanción revocada.' : 'Sanción confirmada.',
        handleReload,
      ),
    [action, handleReload, token],
  );
  return { ...loader, action, handleDismiss, handleSanction, handleAppealDecision };
}

export interface BlocksController extends Loader<BlockedTeam[]> {
  action: Action;
  handleUnblock: (otherId: number) => Promise<void>;
}

export function useBlocks(token: string, teamId: number): BlocksController {
  const action = useAction();
  const loader = useLoader(
    () => moderationApi.blocks(token, teamId),
    (items) => items.length === 0,
    'Tu equipo no ha bloqueado a ningún equipo.',
    `blocks|${teamId}`,
  );
  const { handleReload } = loader;
  const handleUnblock = useCallback(
    (otherId: number) =>
      action.run(() => moderationApi.unblock(token, teamId, otherId), 'Equipo desbloqueado.', handleReload),
    [action, handleReload, teamId, token],
  );
  return { ...loader, action, handleUnblock };
}
