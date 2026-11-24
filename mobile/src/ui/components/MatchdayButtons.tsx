// Accesos del día del partido en el contrato: convocatoria (antes) y valorar compañeros (después).

import type { Contract } from '../../domain/contractModels';
import { PrimaryButton } from './PrimaryButton';

interface Props {
  contract: Contract;
  onCallUp: (contract: Contract) => void;
  onRate: (contract: Contract) => void;
}

export function MatchdayButtons({ contract, onCallUp, onRate }: Props) {
  if (contract.status === 'CANCELLED') return null;
  return (
    <>
      <PrimaryButton label="Convocatoria" variant="secondary" onPress={() => onCallUp(contract)} />
      {contract.result?.status === 'CONFIRMED' ? (
        <PrimaryButton label="Valorar compañeros" variant="secondary" onPress={() => onRate(contract)} />
      ) : null}
    </>
  );
}
