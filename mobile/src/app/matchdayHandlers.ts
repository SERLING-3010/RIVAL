// A dónde lleva cada acceso del día del partido desde el contrato.

import type { Navigator } from '../controllers/useNavigator';
import type { Contract } from '../domain/contractModels';
import type { MatchdayHandlers } from '../ui/components/MatchdayButtons';

const myTeamId = (c: Contract) => (c.my_side === 'HOST' ? c.host.id : c.guest.id);
const rivalTeamId = (c: Contract) => (c.my_side === 'HOST' ? c.guest.id : c.host.id);

export function matchdayHandlers(navigator: Navigator): MatchdayHandlers {
  return {
    onChat: (c) => navigator.push({ name: 'chat', contractId: c.id }),
    onCheckIn: (c) => navigator.push({ name: 'checkIn', contractId: c.id }),
    onTactics: (c) => navigator.push({ name: 'tactics', contractId: c.id }),
    onCallUp: (c) =>
      navigator.push({ name: 'callup', contractId: c.id, teamId: myTeamId(c), isAdmin: c.is_staff }),
    onRate: (c) => navigator.push({ name: 'rate', contractId: c.id }),
    onLoan: (c) =>
      navigator.push({ name: 'loanRequest', contractId: c.id, teamId: myTeamId(c), rivalId: rivalTeamId(c) }),
  };
}
