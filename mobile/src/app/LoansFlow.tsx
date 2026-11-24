// Composición de los Sprints 13 y 14: préstamos y chat del partido.

import { useLoanRequest, useMyLoans } from '../controllers/useLoans';
import { useMatchChat } from '../controllers/useMatchChat';
import { LoanRequestScreen } from '../ui/screens/LoanRequestScreen';
import { LoansScreen } from '../ui/screens/LoansScreen';
import { MatchChatScreen } from '../ui/screens/MatchChatScreen';
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
