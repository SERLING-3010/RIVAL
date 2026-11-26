// Sesión: restaura el token guardado, registra, inicia y cierra sesión.

import { useCallback, useEffect, useState } from 'react';

import { toAppError } from '../domain/appError';
import type { RegisterPayload, SessionResponse, User } from '../domain/models';
import { accountApi } from '../services/accountApi';
import { authApi } from '../services/authApi';
import { pushApi } from '../services/pushApi';
import { registeredToken } from '../services/pushDevice';
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
  handleAcceptTerms: (version: string) => Promise<void>; // Sprint 27
  handleAccountDeleted: () => Promise<void>;
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
      const device = registeredToken(); // Sprint 24: este teléfono deja de recibir avisos de la cuenta
      if (device) await pushApi.remove(token, device).catch(() => undefined);
      await authApi.logout(token).catch(() => undefined);
    }
    await clearToken().catch(() => undefined);
    setToken(null);
    setUser(null);
    setStatus('signedOut');
  }, [token]);

  const handleAcceptTerms = useCallback(
    async (version: string) => {
      if (token) setUser(await accountApi.acceptTerms(token, version));
    },
    [token],
  );

  // La cuenta ya no existe en el servidor: solo se limpia el teléfono.
  const handleAccountDeleted = useCallback(async () => {
    await clearToken().catch(() => undefined);
    setToken(null);
    setUser(null);
    setStatus('signedOut');
  }, []);

  return {
    status,
    user,
    token,
    handleRegister,
    handleLogin,
    handleLogout,
    handleAcceptTerms,
    handleAccountDeleted,
  };
}
