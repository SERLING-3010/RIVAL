// Composición de los Sprints 13 a 15 y 19: préstamos, chat, check-in y alineación táctica.

import { useCheckIn } from '../controllers/useCheckIn';
import { useLoanRequest, useMyLoans } from '../controllers/useLoans';
import { useMatchChat } from '../controllers/useMatchChat';
import { useTactics } from '../controllers/useTactics';
import { CheckInScreen } from '../ui/screens/CheckInScreen';
import { LoanRequestScreen } from '../ui/screens/LoanRequestScreen';
import { LoansScreen } from '../ui/screens/LoansScreen';
import { MatchChatScreen } from '../ui/screens/MatchChatScreen';
import { TacticsScreen } from '../ui/screens/TacticsScreen';
import type { MatchCtx } from './MatchFlow';

export function LoanRequest({
  token,
  navigator,
  contractId,
  teamId,
  rivalId,
}: MatchCtx & { contractId: number; teamId: number; rivalId: number }) {
  return (
    <LoanRequestScreen
      controller={useLoanRequest(token, contractId, teamId, rivalId)}
      onBack={navigator.goBack}
    />
  );
}

export function MyLoans({ token, navigator }: MatchCtx) {
  return <LoansScreen controller={useMyLoans(token)} onBack={navigator.goBack} />;
}

export function MatchChat({ token, navigator, contractId }: MatchCtx & { contractId: number }) {
  return <MatchChatScreen controller={useMatchChat(token, contractId)} onBack={navigator.goBack} />;
}

export function CheckIn({ token, navigator, contractId }: MatchCtx & { contractId: number }) {
  return <CheckInScreen controller={useCheckIn(token, contractId)} onBack={navigator.goBack} />;
}

export function Tactics({ token, navigator, contractId }: MatchCtx & { contractId: number }) {
  return <TacticsScreen controller={useTactics(token, contractId)} onBack={navigator.goBack} />;
}
