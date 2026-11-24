// Composición del Sprint 13: pedir un jugador prestado y decidir préstamos.

import { useLoanRequest, useMyLoans } from '../controllers/useLoans';
import { LoanRequestScreen } from '../ui/screens/LoanRequestScreen';
import { LoansScreen } from '../ui/screens/LoansScreen';
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
