// Check-in en la cancha (Sprint 15): solo "llegó" y la hora; nunca la posición de nadie.

export interface CheckInItem {
  user_id: number;
  display_name: string;
  checked_in_at: string;
}

export interface CheckInBoard {
  contract_id: number;
  unavailable: string | null;
  venue_name: string | null;
  opens_at: string;
  closes_at: string;
  window_open: boolean;
  me_checked_in: boolean;
  items: CheckInItem[];
}

export type CheckInStep = 'unavailable' | 'done' | 'open' | 'notYet' | 'closed';

/** Qué puede hacer la persona ahora con el check-in de este partido. */
export function checkInStep(board: CheckInBoard, now: Date): CheckInStep {
  if (board.unavailable !== null) return 'unavailable';
  if (board.me_checked_in) return 'done';
  if (board.window_open) return 'open';
  return now.getTime() < Date.parse(board.opens_at) ? 'notYet' : 'closed';
}
