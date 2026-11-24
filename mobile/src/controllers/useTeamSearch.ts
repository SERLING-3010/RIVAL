// Buscar equipo por deporte, ciudad y nombre, con "Cargar más", y pedir unirse.
// Nunca hay ubicación exacta: solo ciudad y barrio.

import { useCallback, useEffect, useRef, useState } from 'react';

import { errorToViewState, toAppError } from '../domain/appError';
import type { TeamPage, TeamRole } from '../domain/models';
import type { ViewState } from '../domain/viewState';
import { successOrEmpty } from '../domain/viewState';
import { teamApi } from '../services/teamApi';

export type JoinStatus =
  { kind: 'sending' } | { kind: 'sent'; message: string } | { kind: 'failed'; message: string };

export interface TeamSearchController {
  sport: string | null;
  city: string;
  text: string;
  state: ViewState<TeamPage>;
  hasMore: boolean;
  loadingMore: boolean;
  joinStatus: Record<number, JoinStatus>;
  handleSport: (code: string | null) => void;
  handleCity: (value: string) => void;
  handleText: (value: string) => void;
  handleSearch: () => void;
  handleLoadMore: () => Promise<void>;
  handleRequestJoin: (teamId: number, role: TeamRole) => Promise<void>;
}

const EMPTY_MESSAGE = 'No encontramos equipos con esos filtros. Prueba otra ciudad o crea el tuyo.';
const SENT_MESSAGE = 'Solicitud enviada. El DT o capitán debe aprobarla.';

export function useTeamSearch(token: string, defaultCity: string): TeamSearchController {
  const [sport, setSport] = useState<string | null>(null);
  const [city, setCity] = useState(defaultCity);
  const [text, setText] = useState('');
  const [state, setState] = useState<ViewState<TeamPage>>({ kind: 'loading' });
  const [loadingMore, setLoadingMore] = useState(false);
  const [joinStatus, setJoinStatus] = useState<Record<number, JoinStatus>>({});
  const [attempt, setAttempt] = useState(0);
  const joining = useRef(new Set<number>());

  const query = useCallback(
    (page: number) =>
      teamApi.search(token, {
        sport: sport ?? undefined,
        city: city.trim() || undefined,
        q: text.trim() || undefined,
        page,
      }),
    [token, sport, city, text],
  );

  useEffect(() => {
    let active = true;
    setState({ kind: 'loading' });
    query(1)
      .then((page) => {
        if (active) setState(successOrEmpty(page, page.items.length === 0, EMPTY_MESSAGE));
      })
      .catch((error: unknown) => {
        if (active) setState(errorToViewState<TeamPage>(error));
      });
    return () => {
      active = false;
    };
    // Ciudad y texto no disparan la búsqueda a propósito: se busca al pulsar Buscar
    // o al cambiar de deporte, no en cada letra (evita llamadas duplicadas).
  }, [token, sport, attempt]);

  const current = state.kind === 'success' ? state.data : null;
  const hasMore = current !== null && current.items.length < current.total;

  const handleLoadMore = useCallback(async () => {
    if (!current || loadingMore || !hasMore) return;
    setLoadingMore(true);
    try {
      const next = await query(current.page + 1);
      const known = new Set(current.items.map((t) => t.id));
      setState({
        kind: 'success',
        data: { ...next, items: [...current.items, ...next.items.filter((t) => !known.has(t.id))] },
      });
    } catch (error) {
      setState(errorToViewState<TeamPage>(error));
    } finally {
      setLoadingMore(false);
    }
  }, [current, hasMore, loadingMore, query]);

  const handleRequestJoin = useCallback(
    async (teamId: number, role: TeamRole) => {
      if (joining.current.has(teamId)) return;
      joining.current.add(teamId);
      setJoinStatus((s) => ({ ...s, [teamId]: { kind: 'sending' } }));
      try {
        await teamApi.requestJoin(token, teamId, role);
        setJoinStatus((s) => ({ ...s, [teamId]: { kind: 'sent', message: SENT_MESSAGE } }));
      } catch (error) {
        const appError = toAppError(error);
        // 409 "ya enviaste una solicitud" significa que la solicitud sí existe.
        const status: JoinStatus =
          appError.code === 'REQUEST_ALREADY_PENDING'
            ? { kind: 'sent', message: SENT_MESSAGE }
            : { kind: 'failed', message: appError.message };
        setJoinStatus((s) => ({ ...s, [teamId]: status }));
      } finally {
        joining.current.delete(teamId);
      }
    },
    [token],
  );

  return {
    sport,
    city,
    text,
    state,
    hasMore,
    loadingMore,
    joinStatus,
    handleSport: setSport,
    handleCity: setCity,
    handleText: setText,
    handleSearch: useCallback(() => setAttempt((n) => n + 1), []),
    handleLoadMore,
    handleRequestJoin,
  };
}
