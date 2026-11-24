import { Alert, StyleSheet, Text } from 'react-native';

import type { OffersController } from '../../controllers/useMatches';
import { formatLocal } from '../../domain/dateTime';
import { OFFER_STATUS_LABEL, PLACE_LABEL, REFEREE_LABEL } from '../../domain/matchLabels';
import type { Offer } from '../../domain/matchModels';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { colors, font } from '../theme';

interface Props {
  controller: OffersController;
  isRequestAdmin: boolean;
  myTeamIds: number[];
  requestOpen: boolean;
  onBack: () => void;
}

export function OffersScreen({ controller, isRequestAdmin, myTeamIds, requestOpen, onBack }: Props) {
  const busy = controller.action.busy;
  const canAct = (offer: Offer) => requestOpen && offer.status === 'PENDING';
  const confirmAccept = (offer: Offer) =>
    Alert.alert(`¿Jugar contra ${offer.team.name}?`, 'Las demás ofertas quedarán reemplazadas.', [
      { text: 'Cancelar', style: 'cancel' },
      { text: 'Aceptar', onPress: () => void controller.handleDecide(offer.id, 'accept') },
    ]);
  return (
    <Screen title="Ofertas" onBack={onBack}>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(offers) =>
          offers.map((offer) => (
            <Card
              key={offer.id}
              title={`${offer.team.name} · ${formatLocal(offer.proposed_start)}`}
              subtitle={`${REFEREE_LABEL[offer.referee_mode]} · ${PLACE_LABEL[offer.place_kind]}${offer.place_note ? ` · ${offer.place_note}` : ''}`}
              badge={`${OFFER_STATUS_LABEL[offer.status]}${offer.version > 1 ? ` · v${offer.version}` : ''}`}
            >
              {offer.message ? <Text style={styles.meta}>“{offer.message}”</Text> : null}
              {isRequestAdmin && canAct(offer) ? (
                <>
                  <PrimaryButton label="Aceptar" disabled={busy} onPress={() => confirmAccept(offer)} />
                  <PrimaryButton
                    label="Rechazar"
                    variant="secondary"
                    disabled={busy}
                    onPress={() => void controller.handleDecide(offer.id, 'reject')}
                  />
                </>
              ) : null}
              {!isRequestAdmin && canAct(offer) && myTeamIds.includes(offer.team.id) ? (
                <PrimaryButton
                  label="Retirar oferta"
                  variant="secondary"
                  disabled={busy}
                  onPress={() => void controller.handleDecide(offer.id, 'withdraw')}
                />
              ) : null}
            </Card>
          ))
        }
      </StateView>
      {controller.action.message ? (
        <Text style={styles.message} accessibilityLiveRegion="polite">
          {controller.action.message}
        </Text>
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  meta: { color: colors.textMuted, fontSize: font.small },
  message: { color: colors.text, fontSize: font.body },
});
