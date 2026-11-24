// Partidos pactados del equipo y detalle de un contrato con sus acciones.

import { useCallback, useState } from 'react';

import { termsFromForm } from '../domain/contractForm';
import type { ContractForm } from '../domain/contractForm';
import type { Contract, ContractSummary } from '../domain/contractModels';
import { contractApi } from '../services/contractApi';
import type { Action } from './useAction';
import { useAction } from './useAction';
import type { Loader } from './useLoader';
import { useLoader } from './useLoader';

export function useTeamContracts(token: string, teamId: number): Loader<ContractSummary[]> {
  return useLoader(
    () => contractApi.forTeam(token, teamId),
    (items) => items.length === 0,
    'Tu equipo aún no tiene partidos pactados. Acepta una oferta o haz una para empezar.',
    `contracts|${teamId}`,
  );
}

export interface ContractController extends Loader<Contract> {
  action: Action;
  handleSign: (version: number) => Promise<void>;
  handleRejectAmendment: (version: number) => Promise<void>;
  handleCancel: (reason: string) => Promise<void>;
}

export function useContract(token: string, contractId: number): ContractController {
  const action = useAction();
  const loader = useLoader(
    () => contractApi.get(token, contractId),
    () => false,
    '',
    `contract|${contractId}`,
  );
  const { handleReload } = loader;
  const handleSign = useCallback(
    (version: number) =>
      action.run(() => contractApi.sign(token, contractId, version), 'Firmaste esta versión.', handleReload),
    [action, contractId, handleReload, token],
  );
  const handleRejectAmendment = useCallback(
    (version: number) =>
      action.run(
        () => contractApi.rejectAmendment(token, contractId, version),
        'Cambio descartado. Sigue valiendo la versión firmada.',
        handleReload,
      ),
    [action, contractId, handleReload, token],
  );
  const handleCancel = useCallback(
    (reason: string) =>
      action.run(() => contractApi.cancel(token, contractId, reason), 'Partido cancelado.', handleReload),
    [action, contractId, handleReload, token],
  );
  return { ...loader, action, handleSign, handleRejectAmendment, handleCancel };
}

export interface ProposalController {
  form: ContractForm;
  error: string | null;
  action: Action;
  handleChange: <K extends keyof ContractForm>(field: K, value: ContractForm[K]) => void;
  handleSubmit: () => Promise<void>;
}

export function useContractProposal(
  token: string,
  contract: Contract,
  initial: ContractForm,
  onDone: () => void,
): ProposalController {
  const [form, setForm] = useState<ContractForm>(initial);
  const [error, setError] = useState<string | null>(null);
  const action = useAction();
  const handleChange = useCallback(<K extends keyof ContractForm>(field: K, value: ContractForm[K]) => {
    setForm((f) => ({ ...f, [field]: value }));
    setError(null);
  }, []);
  const handleSubmit = useCallback(async () => {
    const result = termsFromForm(form, new Date());
    if (!result.ok) {
      setError(result.error);
      return;
    }
    await action.run(
      () =>
        contractApi.propose(
          token,
          contract.id,
          contract.current.version,
          result.terms,
          form.note.trim() || null,
        ),
      'Propuesta enviada y firmada por tu equipo. Falta la firma del rival.',
      onDone,
    );
  }, [action, contract.current.version, contract.id, form, onDone, token]);
  return { form, error, action, handleChange, handleSubmit };
}
