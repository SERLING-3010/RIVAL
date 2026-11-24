// Los 7 estados obligatorios de toda vista que lee o cambia datos.

export type ViewState<T> =
  | { kind: 'loading' }
  | { kind: 'empty'; message: string }
  | { kind: 'error'; message: string; correlationId: string | null }
  | { kind: 'success'; data: T }
  | { kind: 'offline'; message: string }
  | { kind: 'conflict'; message: string }
  | { kind: 'approvalGate'; message: string };

export const loadingState = <T>(): ViewState<T> => ({ kind: 'loading' });

export const successOrEmpty = <T>(data: T, isEmpty: boolean, emptyMessage: string): ViewState<T> =>
  isEmpty ? { kind: 'empty', message: emptyMessage } : { kind: 'success', data };
