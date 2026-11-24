import type { Contract } from '../domain/contractModels';
import type { CreateVenuePayload, VenueDetail, VenuePage, VenueSummary } from '../domain/venueModels';
import { request } from './httpClient';

export const venueApi = {
  create: (token: string, payload: CreateVenuePayload) =>
    request<VenueDetail>('POST', '/api/v1/venues', { token, body: payload }),

  search: (token: string, city: string, sport: string) =>
    request<VenuePage>('GET', '/api/v1/venues', { token, query: { city, sport } }),

  mine: (token: string) => request<VenueSummary[]>('GET', '/api/v1/me/venues', { token }),

  get: (token: string, venueId: number) =>
    request<VenueDetail>('GET', `/api/v1/venues/${venueId}`, { token }),

  addCourt: (token: string, venueId: number, name: string, sportCode: string, surface: string | null) =>
    request<VenueDetail>('POST', `/api/v1/venues/${venueId}/courts`, {
      token,
      body: { name, sport_code: sportCode, surface },
    }),

  addSlot: (token: string, courtId: number, startsAt: string, endsAt: string) =>
    request<VenueDetail>('POST', `/api/v1/courts/${courtId}/slots`, {
      token,
      body: { starts_at: startsAt, ends_at: endsAt },
    }),

  decide: (token: string, bookingId: number, decision: 'confirm' | 'reject') =>
    request<VenueDetail>('POST', `/api/v1/bookings/${bookingId}/${decision}`, { token }),

  book: (token: string, contractId: number, slotId: number) =>
    request<Contract>('POST', `/api/v1/contracts/${contractId}/bookings`, {
      token,
      body: { slot_id: slotId },
    }),

  cancelBooking: (token: string, bookingId: number) =>
    request<Contract>('POST', `/api/v1/bookings/${bookingId}/cancel`, { token }),
};
