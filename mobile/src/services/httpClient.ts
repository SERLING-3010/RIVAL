// Cliente HTTP único: tiempo límite, token de sesión y errores comprensibles.

import { AppError, networkError } from '../domain/appError';
import { API_BASE_URL, REQUEST_TIMEOUT_MS } from './config';

type Method = 'GET' | 'POST';

interface ErrorBody {
  code?: string;
  message?: string;
  correlation_id?: string;
  details?: string[];
}

let unauthorizedHandler: (() => void) | null = null;

/** La sesión registra aquí qué hacer si el servidor dice que el token ya no sirve. */
export function setUnauthorizedHandler(handler: (() => void) | null): void {
  unauthorizedHandler = handler;
}

function isErrorBody(value: unknown): value is ErrorBody {
  return typeof value === 'object' && value !== null && 'code' in value;
}

export async function request<T>(
  method: Method,
  path: string,
  options: { body?: unknown; token?: string | null; query?: Record<string, string | undefined> } = {},
): Promise<T> {
  const params = Object.entries(options.query ?? {})
    .filter((entry): entry is [string, string] => entry[1] !== undefined && entry[1] !== '')
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    .join('&');
  const url = `${API_BASE_URL}${path}${params ? `?${params}` : ''}`;
  const headers: Record<string, string> = { Accept: 'application/json' };
  if (options.body !== undefined) {
    headers['Content-Type'] = 'application/json';
  }
  if (options.token) {
    headers.Authorization = `Bearer ${options.token}`;
  }
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  let response: Response;
  let data: unknown = null;
  try {
    response = await fetch(url, {
      method,
      headers,
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
      signal: controller.signal,
    });
    if (response.status !== 204) {
      data = await response.json().catch(() => null);
    }
  } catch {
    throw networkError();
  } finally {
    clearTimeout(timer);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  if (response.status === 401 && options.token) {
    unauthorizedHandler?.();
  }
  if (!response.ok) {
    const body = isErrorBody(data) ? data : {};
    throw new AppError({
      kind: 'http',
      status: response.status,
      code: body.code ?? 'HTTP_ERROR',
      message: body.message ?? 'No pudimos completar la acción. Inténtalo de nuevo.',
      correlationId: body.correlation_id ?? null,
      fields: body.details ?? [],
    });
  }
  return data as T;
}
