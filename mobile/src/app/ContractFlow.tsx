// Composición de los Sprints 3 y 4: partidos pactados, contrato, propuesta de cambios y actividad.

import type { ActivityScope } from '../controllers/useActivity';
import { useActivity } from '../controllers/useActivity';
import { useContract, useContractProposal, useTeamContracts } from '../controllers/useContracts';
import { formFromTerms } from '../domain/contractForm';
import type { Contract } from '../domain/contractModels';
import { ActivityScreen } from '../ui/screens/ActivityScreen';
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
      onBookVenue={(contract) => {
        const terms = (contract.signed ?? contract.current).terms;
        const match = {
          contractId: contract.id,
          kickoffAt: terms.kickoff_at,
          durationMinutes: terms.duration_minutes,
          sportCode: contract.host.sport_code,
        };
        navigator.push({ name: 'bookVenue', match, city: contract.host.city });
      }}
      onLineup={(contract) => {
        const host = contract.my_side === 'HOST';
        const score = (host ? contract.result?.host_score : contract.result?.guest_score) ?? 0;
        navigator.push({
          name: 'lineup',
          contractId: contract.id,
          teamId: host ? contract.host.id : contract.guest.id,
          teamScore: score,
        });
      }}
      onActivity={(id) =>
        navigator.push({ name: 'activity', scope: 'contracts', id, title: 'Actividad del partido' })
      }
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

export function Activity({
  token,
  navigator,
  scope,
  id,
  title,
}: MatchCtx & { scope: ActivityScope; id: number; title: string }) {
  return (
    <ActivityScreen title={title} controller={useActivity(token, scope, id)} onBack={navigator.goBack} />
  );
}
