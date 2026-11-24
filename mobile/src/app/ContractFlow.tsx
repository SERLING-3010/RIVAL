// Composición del Sprint 3: partidos pactados, contrato y propuesta de cambios.

import { useContract, useContractProposal, useTeamContracts } from '../controllers/useContracts';
import { formFromTerms } from '../domain/contractForm';
import type { Contract } from '../domain/contractModels';
import { ContractScreen } from '../ui/screens/ContractScreen';
import { ContractsScreen } from '../ui/screens/ContractsScreen';
import { ProposeContractScreen } from '../ui/screens/ProposeContractScreen';
import type { MatchCtx } from './MatchFlow';

export function Contracts({ token, navigator, teamId }: MatchCtx & { teamId: number }) {
  return (
    <ContractsScreen
      controller={useTeamContracts(token, teamId)}
      onOpen={(contractId) => navigator.push({ name: 'contract', contractId })}
      onBack={navigator.goBack}
    />
  );
}

export function ContractDetail({ token, navigator, contractId }: MatchCtx & { contractId: number }) {
  return (
    <ContractScreen
      controller={useContract(token, contractId)}
      onPropose={(contract) => navigator.push({ name: 'proposeContract', contract })}
      onBack={navigator.goBack}
    />
  );
}

export function ProposeContract({ token, navigator, contract }: MatchCtx & { contract: Contract }) {
  const controller = useContractProposal(
    token,
    contract,
    formFromTerms(contract.current.terms),
    navigator.goBack,
  );
  return (
    <ProposeContractScreen
      controller={controller}
      hostName={contract.host.name}
      guestName={contract.guest.name}
      onBack={navigator.goBack}
    />
  );
}
