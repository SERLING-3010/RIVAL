// Dirección del backend. Se configura con EXPO_PUBLIC_API_URL (ver mobile/README.md).
// 10.0.2.2 es el computador anfitrión visto desde el emulador de Android.

const DEFAULT_API_URL = 'http://10.0.2.2:8000';

export const API_BASE_URL: string = (process.env.EXPO_PUBLIC_API_URL ?? DEFAULT_API_URL).replace(/\/+$/, '');

export const REQUEST_TIMEOUT_MS = 10_000;
