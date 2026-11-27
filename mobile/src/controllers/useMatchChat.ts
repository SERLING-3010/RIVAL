// Chat del partido: carga, consulta periódica de mensajes nuevos, envío y borrado de los propios.

import { useCallback, useEffect, useRef, useState } from 'react';

import { errorToViewState } from '../domain/appError';
import type { ChatPage } from '../domain/chatModels';
import { CHAT_POLL_MS, draftError, lastId, mergeMessages } from '../domain/chatModels';
import type { ViewState } from '../domain/viewState';
import { chatApi } from '../services/chatApi';
import type { Action } from './useAction';
import { useAction } from './useAction';

export interface MatchChatController {
  state: ViewState<ChatPage>;
  draft: string;
  draftError: string | null;
  action: Action;
  setDraft: (text: string) => void;
  handleSend: () => Promise<void>;
  handleDelete: (messageId: number) => Promise<void>;
  handleReload: () => void;
}

export function useMatchChat(token: string, contractId: number, pollMs = CHAT_POLL_MS): MatchChatController {
  const [state, setState] = useState<ViewState<ChatPage>>({ kind: 'loading' });
  const [draft, setDraft] = useState('');
  const [error, setError] = useState<string | null>(null);
  const action = useAction();
  const page = useRef<ChatPage | null>(null);
  const alive = useRef(true);

  const refresh = useCallback(async () => {
    const before = page.current;
    try {
      const fresh = await chatApi.read(token, contractId, before ? lastId(before.messages) : 0);
      const base = page.current; // lo último, por si otra consulta o un borrado terminó mientras tanto
      const merged = base ? { ...fresh, messages: mergeMessages(base.messages, fresh.messages) } : fresh;
      page.current = merged;
      if (alive.current) setState({ kind: 'success', data: merged });
    } catch (e: unknown) {
      if (alive.current && before === null) setState(errorToViewState<ChatPage>(e)); // con chat ya cargado, se reintenta
    }
  }, [contractId, token]);

  useEffect(() => {
    alive.current = true;
    void refresh();
    const timer = setInterval(() => void refresh(), pollMs);
    return () => {
      alive.current = false;
      clearInterval(timer);
    };
  }, [pollMs, refresh]);

  const handleSend = useCallback(async () => {
    const problem = draftError(draft);
    setError(problem);
    if (problem !== null) return;
    await action.run(
      () => chatApi.send(token, contractId, draft.trim()),
      '',
      () => {
        setDraft('');
        void refresh();
      },
    );
  }, [action, contractId, draft, refresh, token]);

  const handleDelete = useCallback(
    (messageId: number) =>
      action.run(
        () => chatApi.remove(token, messageId),
        'Mensaje eliminado.',
        () => {
          const current = page.current;
          if (current === null) return;
          const messages = current.messages.map((m) =>
            m.id === messageId ? { ...m, deleted: true, body: null } : m,
          );
          page.current = { ...current, messages };
          setState({ kind: 'success', data: page.current });
        },
      ),
    [action, token],
  );

  const handleReload = useCallback(() => {
    page.current = null;
    setState({ kind: 'loading' });
    void refresh();
  }, [refresh]);

  return { state, draft, draftError: error, action, setDraft, handleSend, handleDelete, handleReload };
}
