import { beforeEach, describe, expect, jest, test } from '@jest/globals';
import { renderHook, waitFor } from '@testing-library/react-native';

import { usePushRegistration } from '../src/controllers/usePushRegistration';
import { pushApi } from '../src/services/pushApi';
import * as device from '../src/services/pushDevice';

jest.mock('../src/services/pushDevice', () => ({
  showWhileOpen: jest.fn(),
  onNoticeTapped: jest.fn(() => () => undefined),
  pushToken: jest.fn(async () => 'ExponentPushToken[telefono01]'),
  registeredToken: jest.fn(() => null),
}));
jest.mock('../src/services/pushApi', () => ({
  pushApi: { register: jest.fn(async () => null), remove: jest.fn(async () => null) },
}));

describe('usePushRegistration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('con sesión registra el teléfono; tocar un aviso abre Pendientes', async () => {
    const openPending = jest.fn();
    await renderHook(() => usePushRegistration('sesion-1', openPending));
    await waitFor(() =>
      expect(pushApi.register).toHaveBeenCalledWith('sesion-1', 'ExponentPushToken[telefono01]'),
    );
    const tapped = jest.mocked(device.onNoticeTapped).mock.calls[0]?.[0];
    tapped?.('myCard');
    expect(openPending).toHaveBeenCalledWith('myCard');
  });

  test('sin sesión o sin permiso no registra nada', async () => {
    await renderHook(() => usePushRegistration(null, jest.fn()));
    jest.mocked(device.pushToken).mockResolvedValueOnce(null);
    await renderHook(() => usePushRegistration('sesion-2', jest.fn()));
    await waitFor(() => expect(device.pushToken).toHaveBeenCalledTimes(1));
    expect(pushApi.register).not.toHaveBeenCalled();
  });
});
