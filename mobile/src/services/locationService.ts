// Posición del teléfono una sola vez, solo mientras se usa la app (ADR-004, Sprint 15).
// No se guarda aquí ni en ningún lado: se manda una vez al servidor, que la compara y la descarta.

import * as Location from 'expo-location';

import { AppError } from '../domain/appError';

export interface Position {
  latitude: number;
  longitude: number;
}

const denied = () =>
  new AppError({
    kind: 'http',
    status: 0,
    code: 'LOCATION_DENIED',
    message:
      'Para el check-in, permite la ubicación mientras usas RIVAL. Solo se usa una vez y no se guarda.',
  });

export async function currentPosition(): Promise<Position> {
  const permission = await Location.requestForegroundPermissionsAsync();
  if (permission.status !== 'granted') throw denied();
  const fix = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.High });
  return { latitude: fix.coords.latitude, longitude: fix.coords.longitude };
}
