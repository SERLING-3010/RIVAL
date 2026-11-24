import { useCallback, useState } from 'react';

import { toAppError } from '../domain/appError';
import type { User } from '../domain/models';
import type { FieldErrors } from '../domain/validation';
import { teamApi } from '../services/teamApi';
import { useSubmitLock } from './useSubmitLock';

export interface CreateTeamForm {
  name: string;
  sport: string | null;
  modality: string | null;
  city: string;
  neighborhood: string;
  asCoach: boolean;
}

type Field = keyof CreateTeamForm;

export interface CreateTeamController {
  form: CreateTeamForm;
  errors: FieldErrors<Field>;
  submitError: string | null;
  submitting: boolean;
  handleText: (field: 'name' | 'city' | 'neighborhood', value: string) => void;
  handleSport: (code: string) => void;
  handleModality: (code: string) => void;
  handleAsCoach: (value: boolean) => void;
  handleSubmit: () => Promise<void>;
}

function validate(form: CreateTeamForm): FieldErrors<Field> {
  const errors: FieldErrors<Field> = {};
  if (form.name.trim().length < 2) errors.name = 'Ponle un nombre al equipo (mínimo 2 letras).';
  if (!form.sport) errors.sport = 'Elige el deporte.';
  if (!form.modality) errors.modality = 'Elige la modalidad.';
  if (form.city.trim().length < 2) errors.city = 'Escribe la ciudad.';
  if (form.neighborhood.trim().length < 2) errors.neighborhood = 'Escribe el barrio donde juegan.';
  return errors;
}

export function useCreateTeamForm(
  token: string,
  user: User,
  onCreated: (teamId: number) => void,
): CreateTeamController {
  const [form, setForm] = useState<CreateTeamForm>({
    name: '',
    sport: user.sports[0] ?? null,
    modality: null,
    city: user.city,
    neighborhood: user.neighborhood,
    asCoach: user.roles.includes('COACH'),
  });
  const [errors, setErrors] = useState<FieldErrors<Field>>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const lock = useSubmitLock();

  const handleText = useCallback((field: 'name' | 'city' | 'neighborhood', value: string) => {
    setForm((f) => ({ ...f, [field]: value }));
    setErrors((e) => ({ ...e, [field]: undefined }));
  }, []);

  const handleSubmit = useCallback(async () => {
    await lock(async () => {
      const found = validate(form);
      setErrors(found);
      if (Object.values(found).some(Boolean) || !form.sport || !form.modality) return;
      setSubmitting(true);
      setSubmitError(null);
      try {
        const created = await teamApi.create(token, {
          name: form.name.trim(),
          sport_code: form.sport,
          modality_code: form.modality,
          city: form.city.trim(),
          neighborhood: form.neighborhood.trim(),
          as_coach: form.asCoach,
        });
        onCreated(created.team.id);
      } catch (error) {
        setSubmitError(toAppError(error).message);
      } finally {
        setSubmitting(false);
      }
    });
  }, [form, lock, onCreated, token]);

  return {
    form,
    errors,
    submitError,
    submitting,
    handleText,
    handleSport: (code) => setForm((f) => ({ ...f, sport: code, modality: null })),
    handleModality: (code) => setForm((f) => ({ ...f, modality: code })),
    handleAsCoach: (value) => setForm((f) => ({ ...f, asCoach: value })),
    handleSubmit,
  };
}
