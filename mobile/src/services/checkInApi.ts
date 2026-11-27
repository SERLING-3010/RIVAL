import type { CheckInBoard } from '../domain/checkInModels';
import { request } from './httpClient';
import type { Position } from './locationService';

export const checkInApi = {
  board: (token: string, contractId: number) =>
    request<CheckInBoard>('GET', `/api/v1/contracts/${contractId}/check-ins`, { token }),

  checkIn: (token: string, contractId: number, position: Position) =>
    request<CheckInBoard>('POST', `/api/v1/contracts/${contractId}/check-ins`, { token, body: position }),

  setVenueLocation: (token: string, venueId: number, position: Position) =>
    request<{ has_location: boolean }>('POST', `/api/v1/venues/${venueId}/location`, {
      token,
      body: position,
    }),
};
