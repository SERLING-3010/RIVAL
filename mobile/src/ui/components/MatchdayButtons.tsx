// Accesos del día del partido: chat, convocatoria y préstamos (antes) y valorar compañeros (después).

import type { Contract } from '../../domain/contractModels';
import { PrimaryButton } from './PrimaryButton';

export interface MatchdayHandlers {
  onChat: (contract: Contract) => void;
  onCallUp: (contract: Contract) => void;
  onRate: (contract: Contract) => void;
  onLoan: (contract: Contract) => void;
}

interface Props {
  contract: Contract;
  handlers: MatchdayHandlers;
}

export function MatchdayButtons({ contract, handlers }: Props) {
  const chat = (
    <PrimaryButton label="Chat del partido" variant="secondary" onPress={() => handlers.onChat(contract)} />
  );
  if (contract.status === 'CANCELLED') return chat; // el chat queda de solo lectura
  return (
    <>
      {chat}
      <PrimaryButton label="Convocatoria" variant="secondary" onPress={() => handlers.onCallUp(contract)} />
      {contract.is_admin && !contract.result ? (
        <PrimaryButton
          label="Pedir jugador prestado"
          variant="secondary"
          onPress={() => handlers.onLoan(contract)}
        />
      ) : null}
      {contract.result?.status === 'CONFIRMED' ? (
        <PrimaryButton
          label="Valorar compañeros"
          variant="secondary"
          onPress={() => handlers.onRate(contract)}
        />
      ) : null}
    </>
  );
}
