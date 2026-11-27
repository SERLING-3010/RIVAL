// Especiales ya reveladas (Sprint 23), en el almacenamiento seguro del teléfono. Si falla la lectura,
// se trata como "nada visto": en el peor caso se repite una celebración, nunca se pierde una carta.

import * as SecureStore from 'expo-secure-store';

export async function readSeen(key: string): Promise<string[]> {
  try {
    const raw = await SecureStore.getItemAsync(key);
    const parsed: unknown = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed.filter((x): x is string => typeof x === 'string') : [];
  } catch {
    return [];
  }
}

export async function saveSeen(key: string, codes: string[]): Promise<void> {
  try {
    await SecureStore.setItemAsync(key, JSON.stringify(codes));
  } catch {
    // Sin espacio o sin permiso: la próxima vez se vuelve a mostrar; no es grave.
  }
}
