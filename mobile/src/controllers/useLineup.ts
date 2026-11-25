// Planilla del partido: quién jugó y cuántos goles hizo cada uno (solo con resultado confirmado).

import { useCallback, useState } from 'react';

import type { GoalKind } from '../domain/goalKinds';
import { addKind, removeKindAt } from '../domain/goalKinds';
import { lineupFromForm } from '../domain/managerRules';
import { managerApi } from '../services/managerApi';
import type { Action } from './useAction';
import { useAction } from './useAction';

export interface LineupController {
  played: number[];
  goals: Record<number, string>;
  kinds: Record<number, GoalKind[]>; // goles con tipo, por jugador (Sprint 23)
  error: string | null;
  action: Action;
  handleToggle: (userId: number) => void;
  handleGoals: (userId: number, text: string) => void;
  handleAddKind: (userId: number, kind: GoalKind) => void;
  handleRemoveKind: (userId: number, index: number) => void;
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
  const [kinds, setKinds] = useState<Record<number, GoalKind[]>>({});
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
  const handleAddKind = useCallback(
    (userId: number, kind: GoalKind) => {
      const scored = Number((goals[userId] ?? '').trim() || '0') || 0;
      setKinds((k) => ({ ...k, [userId]: addKind(k[userId] ?? [], kind, scored) }));
    },
    [goals],
  );
  const handleRemoveKind = useCallback((userId: number, index: number) => {
    setKinds((k) => ({ ...k, [userId]: removeKindAt(k[userId] ?? [], index) }));
  }, []);
  const handleSubmit = useCallback(async () => {
    const result = lineupFromForm(played, goals, teamScore, kinds);
    if (!result.ok) {
      setError(result.error);
      return;
    }
    await action.run(
      () => managerApi.lineup(token, contractId, result.players),
      'Planilla guardada. Los goles con tipo esperan la confirmación del rival.',
      onDone,
    );
  }, [action, contractId, goals, kinds, onDone, played, teamScore, token]);
  return {
    played,
    goals,
    kinds,
    error,
    action,
    handleToggle,
    handleGoals,
    handleAddKind,
    handleRemoveKind,
    handleSubmit,
  };
}
