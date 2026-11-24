// El token se guarda en el almacenamiento seguro del sistema (Keychain / Keystore).

import * as SecureStore from 'expo-secure-store';

const TOKEN_KEY = 'rival.session.token';

export async function readToken(): Promise<string | null> {
  return SecureStore.getItemAsync(TOKEN_KEY);
}

export async function saveToken(token: string): Promise<void> {
  await SecureStore.setItemAsync(TOKEN_KEY, token);
}

export async function clearToken(): Promise<void> {
  await SecureStore.deleteItemAsync(TOKEN_KEY);
}
