// Planilla del partido: quién jugó y cuántos goles hizo cada uno (solo con resultado confirmado).

import { useCallback, useState } from 'react';

import { lineupFromForm } from '../domain/managerRules';
import { managerApi } from '../services/managerApi';
import type { Action } from './useAction';
import { useAction } from './useAction';

export interface LineupController {
  played: number[];
  goals: Record<number, string>;
  error: string | null;
  action: Action;
  handleToggle: (userId: number) => void;
  handleGoals: (userId: number, text: string) => void;
  handleSubmit: () => Promise<void>;
}

export function useLineup(
  token: string,
  contractId: number,
  teamScore: number,
  onDone: () => void,
): LineupController {
  const [played, setPlayed] = useState<number[]>([]);
  const [goals, setGoals] = useState<Record<number, string>>({});
  const [error, setError] = useState<string | null>(null);
  const action = useAction();
  const handleToggle = useCallback((userId: number) => {
    setPlayed((p) => (p.includes(userId) ? p.filter((id) => id !== userId) : [...p, userId]));
    setError(null);
  }, []);
  const handleGoals = useCallback((userId: number, text: string) => {
    setGoals((g) => ({ ...g, [userId]: text }));
    setError(null);
  }, []);
  const handleSubmit = useCallback(async () => {
    const result = lineupFromForm(played, goals, teamScore);
    if (!result.ok) {
      setError(result.error);
      return;
    }
    await action.run(
      () => managerApi.lineup(token, contractId, result.players),
      'Planilla guardada. Ya cuenta en las fichas de los jugadores.',
      onDone,
    );
  }, [action, contractId, goals, onDone, played, teamScore, token]);
  return { played, goals, error, action, handleToggle, handleGoals, handleSubmit };
}
