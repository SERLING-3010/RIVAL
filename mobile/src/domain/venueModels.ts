// Establecimientos, canchas, franjas y reservas (Sprint 6).

export type BookingStatus = 'PENDING' | 'CONFIRMED' | 'REJECTED' | 'CANCELLED';

export interface VenueSummary {
  id: number;
  name: string;
  address: string;
  city: string;
  neighborhood: string;
  /** Decimal exacto como texto ("80000.00"); solo de referencia por hora, se paga fuera de la app. */
  reference_price: string | null;
  sports: string[];
}

export interface Court {
  id: number;
  name: string;
  sport_code: string;
  surface: string | null;
}

export interface Slot {
  id: number;
  court_id: number;
  court_name: string;
  sport_code: string;
  starts_at: string;
  ends_at: string;
}

export interface Booking {
  id: number;
  status: BookingStatus;
  contract_id: number;
  venue_id: number;
  venue_name: string;
  address: string;
  slot: Slot;
  host_name: string;
  guest_name: string;
  requested_at: string;
}

export interface VenueDetail {
  venue: VenueSummary;
  is_owner: boolean;
  has_location: boolean;
  courts: Court[];
  slots: Slot[];
  pending_bookings: Booking[];
  confirmed_bookings: Booking[];
}

export interface VenuePage {
  items: VenueSummary[];
  page: number;
  page_size: number;
  total: number;
}

export interface CreateVenuePayload {
  name: string;
  address: string;
  city: string;
  neighborhood: string;
  reference_price: string | null;
}

/** Lo que hace falta saber del partido para buscarle cancha. */
export interface MatchToBook {
  contractId: number;
  kickoffAt: string;
  durationMinutes: number;
  sportCode: string;
}
