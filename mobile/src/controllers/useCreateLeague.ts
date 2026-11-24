// Formulario para crear una liga (Sprint 5).

import { useCallback, useState } from 'react';

import { validateSeason } from '../domain/leagueRules';
import type { User } from '../domain/models';
import { leagueApi } from '../services/leagueApi';
import type { Action } from './useAction';
import { useAction } from './useAction';

export interface LeagueForm {
  name: string;
  sport: string;
  modality: string;
  city: string;
  season: string;
  description: string;
}

export interface CreateLeagueController {
  form: LeagueForm;
  error: string | null;
  action: Action;
  handleChange: <K extends keyof LeagueForm>(field: K, value: LeagueForm[K]) => void;
  handleSubmit: () => Promise<void>;
}

export function useCreateLeague(
  token: string,
  user: User,
  onDone: (leagueId: number) => void,
): CreateLeagueController {
  const [form, setForm] = useState<LeagueForm>({
    name: '',
    sport: user.sports[0] ?? '',
    modality: '',
    city: user.city,
    season: String(new Date().getFullYear()),
    description: '',
  });
  const [error, setError] = useState<string | null>(null);
  const action = useAction();
  const handleChange = useCallback(<K extends keyof LeagueForm>(field: K, value: LeagueForm[K]) => {
    setForm((f) => ({ ...f, [field]: value, ...(field === 'sport' ? { modality: '' } : {}) }));
    setError(null);
  }, []);
  const handleSubmit = useCallback(async () => {
    const problem =
      form.name.trim().length < 3
        ? 'El nombre de la liga debe tener al menos 3 caracteres.'
        : !form.sport || !form.modality
          ? 'Elige el deporte y la modalidad.'
          : validateSeason(form.season);
    if (problem) {
      setError(problem);
      return;
    }
    let createdId = 0;
    await action.run(
      async () => {
        const created = await leagueApi.create(token, {
          name: form.name.trim(),
          sport_code: form.sport,
          modality_code: form.modality,
          city: form.city.trim(),
          season: form.season.trim(),
          description: form.description.trim() || null,
        });
        createdId = created.league.id;
      },
      'Liga creada. Eres su organizador.',
      () => onDone(createdId),
    );
  }, [action, form, onDone, token]);
  return { form, error, action, handleChange, handleSubmit };
}
