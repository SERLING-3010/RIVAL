// Alineación táctica del partido: cargarla y, si eres administrador, guardarla.

import { useCallback } from 'react';

import type { Tactic, TacticDraft } from '../domain/tacticsModels';
import { draftBody, draftProblem } from '../domain/tacticsModels';
import { tacticsApi } from '../services/tacticsApi';
import type { Action } from './useAction';
import { useAction } from './useAction';
import type { Loader } from './useLoader';
import { useLoader } from './useLoader';

export interface TacticsController extends Loader<Tactic> {
  action: Action;
  /** Devuelve lo que impide guardar, o null si se envió. */
  handleSave: (draft: TacticDraft, tactic: Tactic) => Promise<string | null>;
}

export function useTactics(token: string, contractId: number): TacticsController {
  const action = useAction();
  const loader = useLoader(
    () => tacticsApi.get(token, contractId),
    () => false,
    '',
    `tactics|${contractId}`,
  );
  const { handleReload } = loader;
  const handleSave = useCallback(
    async (draft: TacticDraft, tactic: Tactic) => {
      const problem = draftProblem(draft, tactic);
      if (problem !== null) return problem;
      await action.run(
        () => tacticsApi.save(token, contractId, draftBody(draft, tactic)),
        'Alineación guardada. Solo la ve tu equipo.',
        handleReload,
      );
      return null;
    },
    [action, contractId, handleReload, token],
  );
  return { ...loader, action, handleSave };
}
