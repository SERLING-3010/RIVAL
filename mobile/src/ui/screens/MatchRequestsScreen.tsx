import { Alert, StyleSheet, Text } from 'react-native';

import type { MyRequestsController } from '../../controllers/useMatches';
import { formatLocal } from '../../domain/dateTime';
import { PLACE_LABEL, REFEREE_LABEL, REQUEST_STATUS_LABEL, SCOPE_LABEL } from '../../domain/matchLabels';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { colors, font } from '../theme';

interface Props {
  controller: MyRequestsController;
  isAdmin: boolean;
  onCreate: () => void;
  onOpenOffers: (requestId: number, open: boolean) => void;
  onBack: () => void;
}

export function MatchRequestsScreen({ controller, isAdmin, onCreate, onOpenOffers, onBack }: Props) {
  const confirmCancel = (requestId: number) =>
    Alert.alert('¿Cancelar la búsqueda?', 'Las ofertas pendientes también se cancelarán.', [
      { text: 'No', style: 'cancel' },
      {
        text: 'Cancelar búsqueda',
        style: 'destructive',
        onPress: () => void controller.handleCancel(requestId),
      },
    ]);
  return (
    <Screen title="Búsquedas de partido" onBack={onBack}>
      {isAdmin ? <PrimaryButton label="Publicar búsqueda" onPress={onCreate} /> : null}
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(items) =>
          items.map((request) => (
            <Card
              key={request.id}
              title={`${formatLocal(request.window_start)} → ${formatLocal(request.window_end)}`}
              subtitle={`${request.target_team_id ? 'Reto directo' : SCOPE_LABEL[request.scope]} · ${REFEREE_LABEL[request.referee_mode]} · ${PLACE_LABEL[request.place_kind]}`}
              badge={REQUEST_STATUS_LABEL[request.status]}
            >
              <Text style={styles.meta}>{request.pending_offers} oferta(s) pendiente(s)</Text>
              <PrimaryButton
                label="Ver ofertas"
                variant="secondary"
                onPress={() => onOpenOffers(request.id, request.status === 'OPEN')}
              />
              {isAdmin && request.status === 'OPEN' ? (
                <PrimaryButton
                  label="Cancelar búsqueda"
                  variant="danger"
                  disabled={controller.action.busy}
                  onPress={() => confirmCancel(request.id)}
                />
              ) : null}
            </Card>
          ))
        }
      </StateView>
      {controller.action.message ? <Text style={styles.meta}>{controller.action.message}</Text> : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  meta: { color: colors.textMuted, fontSize: font.small },
});
