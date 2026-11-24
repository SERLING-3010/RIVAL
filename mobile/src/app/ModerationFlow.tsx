// Composición del Sprint 12: reportar, mis sanciones, cola de moderación y equipos bloqueados.

import { useBlocks, useModerationMe, useModerationQueue } from '../controllers/useModeration';
import { useReport } from '../controllers/useReport';
import type { ReportTarget } from '../domain/moderationModels';
import { BlockedTeamsScreen } from '../ui/screens/BlockedTeamsScreen';
import { ModerationScreen } from '../ui/screens/ModerationScreen';
import { MySanctionsScreen } from '../ui/screens/MySanctionsScreen';
import { ReportScreen } from '../ui/screens/ReportScreen';
import type { MatchCtx } from './MatchFlow';

export function Report({ token, navigator, target }: MatchCtx & { target: ReportTarget }) {
  return (
    <ReportScreen
      controller={useReport(token, target, navigator.goBack)}
      targetName={target.name}
      onBack={navigator.goBack}
    />
  );
}

export function MySanctions({ token, navigator }: MatchCtx) {
  return <MySanctionsScreen controller={useModerationMe(token)} onBack={navigator.goBack} />;
}

export function Moderation({ token, navigator }: MatchCtx) {
  return <ModerationScreen controller={useModerationQueue(token)} onBack={navigator.goBack} />;
}

export function BlockedTeams({ token, navigator, teamId }: MatchCtx & { teamId: number }) {
  return <BlockedTeamsScreen controller={useBlocks(token, teamId)} onBack={navigator.goBack} />;
}
