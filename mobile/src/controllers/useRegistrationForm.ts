// Formulario de registro: conserva lo escrito si falla y muestra errores por campo.

import { useCallback, useState } from 'react';

import { toAppError } from '../domain/appError';
import type { RegisterPayload, UserRole } from '../domain/models';
import type { FieldErrors, RegistrationForm } from '../domain/validation';
import { parseBirthDate, validateRegistration } from '../domain/validation';
import { useSubmitLock } from './useSubmitLock';

type Field = keyof RegistrationForm;

export interface RegistrationController {
  form: RegistrationForm;
  errors: FieldErrors<Field>;
  submitError: string | null;
  submitting: boolean;
  handleChange: (field: Exclude<Field, 'sports' | 'role'>, value: string) => void;
  handleToggleSport: (code: string) => void;
  handleSubmit: () => Promise<void>;
}

export function useRegistrationForm(
  role: UserRole,
  onRegister: (payload: RegisterPayload) => Promise<void>,
): RegistrationController {
  const [form, setForm] = useState<RegistrationForm>({
    role,
    displayName: '',
    email: '',
    password: '',
    birthDate: '',
    sports: [],
    city: '',
    neighborhood: '',
    position: '',
  });
  const [errors, setErrors] = useState<FieldErrors<Field>>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const lock = useSubmitLock();

  const handleChange = useCallback((field: Exclude<Field, 'sports' | 'role'>, value: string) => {
    setForm((f) => ({ ...f, [field]: value }));
    setErrors((e) => ({ ...e, [field]: undefined }));
  }, []);

  const handleToggleSport = useCallback((code: string) => {
    setForm((f) => ({
      ...f,
      sports: f.sports.includes(code) ? f.sports.filter((s) => s !== code) : [...f.sports, code],
    }));
    setErrors((e) => ({ ...e, sports: undefined }));
  }, []);

  const handleSubmit = useCallback(async () => {
    await lock(async () => {
      const found = validateRegistration(form, new Date());
      setErrors(found);
      if (Object.values(found).some(Boolean)) return;
      setSubmitting(true);
      setSubmitError(null);
      try {
        await onRegister({
          email: form.email.trim(),
          password: form.password,
          display_name: form.displayName.trim(),
          birth_date: parseBirthDate(form.birthDate) ?? '',
          role: form.role,
          sports: form.sports,
          city: form.city.trim(),
          neighborhood: form.neighborhood.trim(),
          position: form.position.trim() || null,
        });
      } catch (error) {
        setSubmitError(toAppError(error).message);
      } finally {
        setSubmitting(false);
      }
    });
  }, [form, lock, onRegister]);

  return { form, errors, submitError, submitting, handleChange, handleToggleSport, handleSubmit };
}
