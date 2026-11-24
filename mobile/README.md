# RIVAL — App móvil

Expo SDK 58 + React Native + TypeScript estricto.

## Capas

- `src/domain`: tipos, validaciones y los 7 estados de vista (`viewState.ts`). Sin React.
- `src/services`: cliente HTTP, API de identidad y equipos, almacenamiento seguro del token.
- `src/controllers`: hooks con el estado y las acciones (`handle*`). Ni HTTP ni SQL en las vistas.
- `src/ui`: componentes y pantallas puras (reciben datos y funciones `on*`).
- `src/app`: composición de pantallas y controladores.

## Conectar con el backend

| Dónde corre la app | Valor de `EXPO_PUBLIC_API_URL` |
| --- | --- |
| Emulador de Android | `http://10.0.2.2:8000` (por defecto; no hay que configurar nada) |
| Teléfono físico en la misma red | `http://<IP-de-tu-PC>:8000` y el backend con `--host 0.0.0.0` |

El modo de teléfono físico expone el backend a tu red local: úsalo solo en una red de confianza y solo para desarrollo.

```powershell
$env:EXPO_PUBLIC_API_URL = "http://192.168.1.50:8000"
npx expo start
```

## Comandos

```powershell
npm ci             # instala exactamente las versiones del package-lock.json
npm run typecheck  # tsc --noEmit
npm test           # reglas locales (node --test) y pruebas de componentes (jest-expo)
npx expo start --android
```

Los iconos de `assets/` son provisionales (una "R" sobre azul).
