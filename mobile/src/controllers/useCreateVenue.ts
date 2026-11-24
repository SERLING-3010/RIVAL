// Formulario para registrar un establecimiento (Sprint 6).

import { useCallback, useState } from 'react';

import type { User } from '../domain/models';
import { parsePrice } from '../domain/venueRules';
import { venueApi } from '../services/venueApi';
import type { Action } from './useAction';
import { useAction } from './useAction';

export interface VenueForm {
  name: string;
  address: string;
  city: string;
  neighborhood: string;
  price: string;
}

export interface CreateVenueController {
  form: VenueForm;
  error: string | null;
  action: Action;
  handleChange: <K extends keyof VenueForm>(field: K, value: VenueForm[K]) => void;
  handleSubmit: () => Promise<void>;
}

export function useCreateVenue(
  token: string,
  user: User,
  onDone: (venueId: number) => void,
): CreateVenueController {
  const [form, setForm] = useState<VenueForm>({
    name: '',
    address: '',
    city: user.city,
    neighborhood: user.neighborhood,
    price: '',
  });
  const [error, setError] = useState<string | null>(null);
  const action = useAction();
  const handleChange = useCallback(<K extends keyof VenueForm>(field: K, value: VenueForm[K]) => {
    setForm((f) => ({ ...f, [field]: value }));
    setError(null);
  }, []);
  const handleSubmit = useCallback(async () => {
    const price = parsePrice(form.price);
    const problem =
      form.name.trim().length < 3
        ? 'El nombre debe tener al menos 3 caracteres.'
        : form.address.trim().length < 5
          ? 'Escribe la dirección del establecimiento.'
          : !price.ok
            ? price.error
            : null;
    if (problem || !price.ok) {
      setError(problem);
      return;
    }
    let createdId = 0;
    await action.run(
      async () => {
        const created = await venueApi.create(token, {
          name: form.name.trim(),
          address: form.address.trim(),
          city: form.city.trim(),
          neighborhood: form.neighborhood.trim(),
          reference_price: price.value,
        });
        createdId = created.venue.id;
      },
      'Establecimiento registrado.',
      () => onDone(createdId),
    );
  }, [action, form, onDone, token]);
  return { form, error, action, handleChange, handleSubmit };
}
