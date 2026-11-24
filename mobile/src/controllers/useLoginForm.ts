import { useCallback, useState } from 'react';

import { toAppError } from '../domain/appError';
import { useSubmitLock } from './useSubmitLock';

export interface LoginController {
  email: string;
  password: string;
  error: string | null;
  submitting: boolean;
  handleEmail: (value: string) => void;
  handlePassword: (value: string) => void;
  handleSubmit: () => Promise<void>;
}

export function useLoginForm(onLogin: (email: string, password: string) => Promise<void>): LoginController {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const lock = useSubmitLock();

  const handleSubmit = useCallback(async () => {
    await lock(async () => {
      if (!email.trim() || !password) {
        setError('Escribe tu correo y tu contraseña.');
        return;
      }
      setSubmitting(true);
      setError(null);
      try {
        await onLogin(email.trim(), password);
      } catch (caught) {
        setError(toAppError(caught).message);
      } finally {
        setSubmitting(false);
      }
    });
  }, [email, lock, onLogin, password]);

  return {
    email,
    password,
    error,
    submitting,
    handleEmail: setEmail,
    handlePassword: setPassword,
    handleSubmit,
  };
}
