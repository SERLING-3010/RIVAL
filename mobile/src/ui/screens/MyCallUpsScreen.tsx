// Mis convocatorias a partidos próximos. Al abrir una, el jugador responde si va.

import type { Loader } from '../../controllers/useLoader';
import { formatLocal } from '../../domain/dateTime';
import type { MyCallUp } from '../../domain/matchdayModels';
import { CALLUP_STATUS_LABEL } from '../../domain/matchdayModels';
import { Card } from '../components/Card';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';

interface Props {
  controller: Loader<MyCallUp[]>;
  onOpen: (contractId: number) => void;
  onBack: () => void;
}

export function MyCallUpsScreen({ controller, onOpen, onBack }: Props) {
  return (
    <Screen title="Mis convocatorias" onBack={onBack}>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(items) =>
          items.map((c) => (
            <Card
              key={c.contract_id}
              title={`${c.my_team} vs ${c.opponent}`}
              subtitle={formatLocal(c.kickoff_at)}
              badge={CALLUP_STATUS_LABEL[c.status]}
              onPress={() => onOpen(c.contract_id)}
            />
          ))
        }
      </StateView>
    </Screen>
  );
}
