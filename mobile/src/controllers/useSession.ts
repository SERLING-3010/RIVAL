// Sesión: restaura el token guardado, registra, inicia y cierra sesión.

import { useCallback, useEffect, useState } from 'react';

import { toAppError } from '../domain/appError';
import type { RegisterPayload, SessionResponse, User } from '../domain/models';
import { authApi } from '../services/authApi';
import { setUnauthorizedHandler } from '../services/httpClient';
import { clearToken, readToken, saveToken } from '../services/tokenStore';

export type SessionStatus = 'restoring' | 'signedOut' | 'signedIn';

export interface Session {
  status: SessionStatus;
  user: User | null;
  token: string | null;
  handleRegister: (payload: RegisterPayload) => Promise<void>;
  handleLogin: (email: string, password: string) => Promise<void>;
  handleLogout: () => Promise<void>;
}

export function useSession(): Session {
  const [status, setStatus] = useState<SessionStatus>('restoring');
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    const restore = async () => {
      try {
        const saved = await readToken();
        if (!saved) {
          if (active) setStatus('signedOut');
          return;
        }
        const me = await authApi.me(saved);
        if (!active) return;
        setUser(me);
        setToken(saved);
        setStatus('signedIn');
      } catch (error) {
        if (toAppError(error).status === 401) await clearToken().catch(() => undefined);
        if (active) setStatus('signedOut');
      }
    };
    void restore();
    return () => {
      active = false;
    };
  }, []);

  // Si el servidor rechaza el token a mitad de uso, se cierra la sesión en todo el app.
  useEffect(() => {
    setUnauthorizedHandler(() => {
      void clearToken().catch(() => undefined);
      setToken(null);
      setUser(null);
      setStatus('signedOut');
    });
    return () => setUnauthorizedHandler(null);
  }, []);

  const accept = useCallback(async (session: SessionResponse) => {
    // Si el almacenamiento seguro falla, la sesión sigue en memoria: la cuenta ya existe.
    await saveToken(session.token).catch(() => undefined);
    setToken(session.token);
    setUser(session.user);
    setStatus('signedIn');
  }, []);

  const handleRegister = useCallback(
    async (payload: RegisterPayload) => accept(await authApi.register(payload)),
    [accept],
  );

  const handleLogin = useCallback(
    async (email: string, password: string) => accept(await authApi.login(email, password)),
    [accept],
  );

  const handleLogout = useCallback(async () => {
    if (token) {
      await authApi.logout(token).catch(() => undefined);
    }
    await clearToken().catch(() => undefined);
    setToken(null);
    setUser(null);
    setStatus('signedOut');
  }, [token]);

  return { status, user, token, handleRegister, handleLogin, handleLogout };
}
