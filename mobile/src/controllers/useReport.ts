// Formulario de reporte de una persona o un equipo (Sprint 12).

import { useCallback, useState } from 'react';

import type { ReportCategory, ReportTarget } from '../domain/moderationModels';
import { textError } from '../domain/moderationModels';
import { moderationApi } from '../services/moderationApi';
import type { Action } from './useAction';
import { useAction } from './useAction';

export interface ReportController {
  category: ReportCategory;
  description: string;
  error: string | null;
  action: Action;
  handleCategory: (category: ReportCategory) => void;
  handleDescription: (text: string) => void;
  handleSubmit: () => Promise<void>;
}

export function useReport(token: string, target: ReportTarget, onDone: () => void): ReportController {
  const [category, setCategory] = useState<ReportCategory>('AGGRESSION');
  const [description, setDescription] = useState('');
  const [error, setError] = useState<string | null>(null);
  const action = useAction();
  const handleSubmit = useCallback(async () => {
    const problem = textError(description, 10, 500, 'La descripción');
    if (problem) {
      setError(problem);
      return;
    }
    setError(null);
    await action.run(
      () =>
        moderationApi.report(token, {
          category,
          description: description.trim(),
          target_user_id: target.kind === 'user' ? target.id : null,
          target_team_id: target.kind === 'team' ? target.id : null,
        }),
      'Reporte enviado. Lo revisará una persona moderadora.',
      onDone,
    );
  }, [action, category, description, onDone, target, token]);
  return {
    category,
    description,
    error,
    action,
    handleCategory: setCategory,
    handleDescription: (text: string) => {
      setDescription(text);
      setError(null);
    },
    handleSubmit,
  };
}
