// Bandeja de pendientes: cada tarjeta lleva al lugar donde se resuelve.

import type { Loader } from '../../controllers/useLoader';
import { formatLocal } from '../../domain/dateTime';
import type { PendingItem } from '../../domain/pendingModels';
import { urgency } from '../../domain/pendingModels';
import { Card } from '../components/Card';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';

interface Props {
  controller: Loader<PendingItem[]>;
  onOpen: (item: PendingItem) => void;
  onBack: () => void;
}

export function PendingScreen({ controller, onOpen, onBack }: Props) {
  const now = new Date();
  return (
    <Screen title="Pendientes" onBack={onBack}>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(items) =>
          items.map((item, i) => (
            <Card
              key={`${item.kind}-${item.target_id ?? 'x'}-${i}`}
              title={item.title}
              subtitle={item.due_at ? `${item.detail} · ${formatLocal(item.due_at)}` : item.detail}
              badge={urgency(item, now)}
              onPress={() => onOpen(item)}
            />
          ))
        }
      </StateView>
    </Screen>
  );
}
