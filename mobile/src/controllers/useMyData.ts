// Mis datos (Sprint 27): descargar lo que RIVAL guarda de ti y eliminar la cuenta (anonimizar).

import { useCallback, useState } from 'react';
import { Linking, Share } from 'react-native';

import { toAppError } from '../domain/appError';
import { accountApi } from '../services/accountApi';
import type { Action } from './useAction';
import { useAction } from './useAction';

export interface MyDataController {
  action: Action;
  password: string;
  error: string | null;
  handlePassword: (text: string) => void;
  handleExport: () => Promise<void>;
  handleDelete: () => Promise<void>;
  handleContact: (mailto: string) => Promise<void>; // Sprint 29: escribir a privacidad
}

export function useMyData(token: string, onDeleted: () => Promise<void>): MyDataController {
  const action = useAction();
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleExport = useCallback(
    () =>
      action.run(async () => {
        const data = await accountApi.exportData(token);
        // Se comparte como texto: la persona decide dónde guardarlo (correo, notas, archivos).
        await Share.share({ title: 'Mis datos en RIVAL', message: JSON.stringify(data, null, 2) });
      }, 'Listo: tus datos están en el menú para compartir.'),
    [action, token],
  );

  const handleDelete = useCallback(async () => {
    if (password.length === 0) {
      setError('Escribe tu contraseña para confirmar.');
      return;
    }
    setError(null);
    try {
      await accountApi.deleteAccount(token, password);
      await onDeleted();
    } catch (e) {
      setError(toAppError(e).message);
    }
  }, [onDeleted, password, token]);

  const handleContact = useCallback(async (mailto: string) => {
    // Abre la app de correo con la solicitud ya armada; la persona revisa y decide si la envía.
    await Linking.openURL(mailto).catch(() =>
      setError('No encontramos una app de correo. Escríbenos desde tu correo a la dirección de privacidad.'),
    );
  }, []);

  return { action, password, error, handlePassword: setPassword, handleExport, handleDelete, handleContact };
}
