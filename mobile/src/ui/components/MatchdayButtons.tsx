// Accesos del día del partido: convocatoria y préstamos (antes) y valorar compañeros (después).

import type { Contract } from '../../domain/contractModels';
import { PrimaryButton } from './PrimaryButton';

interface Props {
  contract: Contract;
  onCallUp: (contract: Contract) => void;
  onRate: (contract: Contract) => void;
  onLoan: (contract: Contract) => void;
}

export function MatchdayButtons({ contract, onCallUp, onRate, onLoan }: Props) {
  if (contract.status === 'CANCELLED') return null;
  return (
    <>
      <PrimaryButton label="Convocatoria" variant="secondary" onPress={() => onCallUp(contract)} />
      {contract.is_admin && !contract.result ? (
        <PrimaryButton label="Pedir jugador prestado" variant="secondary" onPress={() => onLoan(contract)} />
      ) : null}
      {contract.result?.status === 'CONFIRMED' ? (
        <PrimaryButton label="Valorar compañeros" variant="secondary" onPress={() => onRate(contract)} />
      ) : null}
    </>
  );
}
