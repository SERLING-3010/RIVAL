import type { ViewState } from './viewState';

export type AppErrorKind = 'network' | 'http';

export class AppError extends Error {
  readonly kind: AppErrorKind;
  readonly status: number;
  readonly code: string;
  readonly correlationId: string | null;
  readonly fields: string[];

  constructor(params: {
    kind: AppErrorKind;
    status: number;
    code: string;
    message: string;
    correlationId?: string | null;
    fields?: string[];
  }) {
    super(params.message);
    this.kind = params.kind;
    this.status = params.status;
    this.code = params.code;
    this.correlationId = params.correlationId ?? null;
    this.fields = params.fields ?? [];
  }
}

const OFFLINE_MESSAGE = 'Sin conexión. No se guardó nada; vuelve a intentarlo cuando tengas señal.';
const UNKNOWN_MESSAGE = 'Algo salió mal. Inténtalo de nuevo en un momento.';

export function toAppError(error: unknown): AppError {
  if (error instanceof AppError) {
    return error;
  }
  return new AppError({ kind: 'http', status: 0, code: 'UNKNOWN', message: UNKNOWN_MESSAGE });
}

export function errorToViewState<T>(error: unknown): ViewState<T> {
  const appError = toAppError(error);
  if (appError.kind === 'network') {
    return { kind: 'offline', message: OFFLINE_MESSAGE };
  }
  if (appError.status === 409) {
    return { kind: 'conflict', message: appError.message };
  }
  if (appError.status === 403) {
    return { kind: 'approvalGate', message: appError.message };
  }
  return { kind: 'error', message: appError.message, correlationId: appError.correlationId };
}

export function networkError(): AppError {
  return new AppError({ kind: 'network', status: 0, code: 'OFFLINE', message: OFFLINE_MESSAGE });
}
