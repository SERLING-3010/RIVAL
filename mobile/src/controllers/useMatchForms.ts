// Formularios: publicar una búsqueda de partido (o retar) y hacer una oferta.

import { useCallback, useState } from 'react';

import { localTextInDays, isoToLocalText, parseLocalDateTime } from '../domain/dateTime';
import type { MatchRequest, PlaceKind, RefereeMode, SearchScope } from '../domain/matchModels';
import { matchApi } from '../services/matchApi';
import type { Action } from './useAction';
import { useAction } from './useAction';

export interface RequestForm {
  start: string;
  end: string;
  scope: SearchScope;
  radiusKm: number;
  referee: RefereeMode;
  place: PlaceKind;
  placeNote: string;
  message: string;
}

export interface FormController<F> {
  form: F;
  error: string | null;
  action: Action;
  handleChange: <K extends keyof F>(field: K, value: F[K]) => void;
  handleSubmit: () => Promise<void>;
}

function useForm<F>(initial: F) {
  const [form, setForm] = useState<F>(initial);
  const [error, setError] = useState<string | null>(null);
  const handleChange = useCallback(<K extends keyof F>(field: K, value: F[K]) => {
    setForm((f) => ({ ...f, [field]: value }));
    setError(null);
  }, []);
  return { form, error, setError, handleChange };
}

export function useCreateMatchRequest(
  token: string,
  teamId: number,
  targetTeamId: number | null,
  onDone: () => void,
): FormController<RequestForm> {
  const now = new Date();
  const { form, error, setError, handleChange } = useForm<RequestForm>({
    start: localTextInDays(now, 1, 8),
    end: localTextInDays(now, 3, 20),
    scope: targetTeamId ? 'CITY' : 'NEARBY',
    radiusKm: 5,
    referee: 'EITHER',
    place: 'TO_AGREE',
    placeNote: '',
    message: '',
  });
  const action = useAction();
  const handleSubmit = useCallback(async () => {
    const start = parseLocalDateTime(form.start);
    const end = parseLocalDateTime(form.end);
    if (!start || !end) {
      setError('Escribe las fechas como dd/mm/aaaa hh:mm, por ejemplo 28/11/2026 18:00.');
      return;
    }
    await action.run(
      () =>
        matchApi.create(token, teamId, {
          window_start: start,
          window_end: end,
          scope: form.scope,
          radius_km: form.scope === 'NEARBY' ? form.radiusKm : null,
          target_team_id: targetTeamId,
          referee_mode: form.referee,
          place_kind: form.place,
          place_note: form.placeNote.trim() || null,
          message: form.message.trim() || null,
        }),
      targetTeamId ? 'Reto enviado.' : 'Búsqueda publicada.',
      onDone,
    );
  }, [action, form, onDone, setError, targetTeamId, teamId, token]);
  return { form, error, action, handleChange, handleSubmit };
}

export interface OfferForm {
  start: string;
  referee: Exclude<RefereeMode, 'EITHER'>;
  place: PlaceKind;
  placeNote: string;
  message: string;
}

export function useOfferForm(
  token: string,
  teamId: number,
  request: MatchRequest,
  onDone: () => void,
): FormController<OfferForm> {
  const { form, error, setError, handleChange } = useForm<OfferForm>({
    // Nunca proponer por defecto una hora pasada: el inicio de la ventana o dentro de una hora.
    start: isoToLocalText(
      new Date(Math.max(Date.parse(request.window_start), Date.now() + 3_600_000)).toISOString(),
    ),
    referee: request.referee_mode === 'WITH' ? 'WITH' : 'WITHOUT',
    place: request.place_kind,
    placeNote: request.place_note ?? '',
    message: '',
  });
  const action = useAction();
  const handleSubmit = useCallback(async () => {
    const start = parseLocalDateTime(form.start);
    if (!start) {
      setError('Escribe la fecha como dd/mm/aaaa hh:mm.');
      return;
    }
    await action.run(
      () =>
        matchApi.offer(token, teamId, request.id, {
          proposed_start: start,
          referee_mode: form.referee,
          place_kind: form.place,
          place_note: form.placeNote.trim() || null,
          message: form.message.trim() || null,
        }),
      'Oferta enviada. Si envías otra, reemplaza a esta.',
      onDone,
    );
  }, [action, form, onDone, request.id, setError, teamId, token]);
  return { form, error, action, handleChange, handleSubmit };
}
