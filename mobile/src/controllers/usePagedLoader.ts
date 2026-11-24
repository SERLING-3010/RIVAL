// Carga paginada con "Cargar más": acumula páginas y se reinicia cuando cambia la consulta.

import { useCallback, useEffect, useState } from 'react';

import { toAppError } from '../domain/appError';
import type { ViewState } from '../domain/viewState';
import { useLoader } from './useLoader';
import { useSubmitLock } from './useSubmitLock';

export interface Page<T> {
  items: T[];
  page: number;
  page_size: number;
  total: number;
}

export interface PagedLoader<T> {
  state: ViewState<Page<T>>;
  hasMore: boolean;
  loadingMore: boolean;
  moreError: string | null;
  handleReload: () => void;
  handleLoadMore: () => Promise<void>;
}

export function usePagedLoader<T>(
  load: (page: number) => Promise<Page<T>>,
  emptyMessage: string,
  key: string,
): PagedLoader<T> {
  const first = useLoader(
    () => load(1),
    (p) => p.items.length === 0,
    emptyMessage,
    key,
  );
  const [extra, setExtra] = useState<T[]>([]);
  const [lastPage, setLastPage] = useState(1);
  const [loadingMore, setLoadingMore] = useState(false);
  const [moreError, setMoreError] = useState<string | null>(null);
  const lock = useSubmitLock();

  useEffect(() => {
    setExtra([]);
    setLastPage(1);
    setMoreError(null);
  }, [key, first.state.kind]);

  const base = first.state.kind === 'success' ? first.state.data : null;
  const items = base ? [...base.items, ...extra] : [];
  const hasMore = base !== null && items.length < base.total;
  const state: ViewState<Page<T>> = base ? { kind: 'success', data: { ...base, items } } : first.state;

  const handleLoadMore = useCallback(async () => {
    if (!hasMore) return;
    await lock(async () => {
      setLoadingMore(true);
      setMoreError(null);
      try {
        const next = await load(lastPage + 1);
        setExtra((current) => [...current, ...next.items]);
        setLastPage(next.page);
      } catch (error) {
        setMoreError(toAppError(error).message);
      } finally {
        setLoadingMore(false);
      }
    });
  }, [hasMore, lastPage, load, lock]);

  return { state, hasMore, loadingMore, moreError, handleReload: first.handleReload, handleLoadMore };
}
