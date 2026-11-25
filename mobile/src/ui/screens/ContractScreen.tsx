import { useState } from 'react';
import { Alert, StyleSheet, Text } from 'react-native';

import type { ContractController } from '../../controllers/useContracts';
import type { Contract } from '../../domain/contractModels';
import { CONTRACT_STATUS_LABEL, contractActions } from '../../domain/contractRules';
import { BookingCard } from '../components/BookingCard';
import type { MatchdayHandlers } from '../components/MatchdayButtons';
import { MatchdayButtons } from '../components/MatchdayButtons';
import { ContractVersionCard as VersionCard } from '../components/ContractVersionCard';
import { PrimaryButton } from '../components/PrimaryButton';
import { ResultPanel } from '../components/ResultPanel';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { TextField } from '../components/TextField';
import { colors, font } from '../theme';

interface Props {
  controller: ContractController;
  onPropose: (contract: Contract) => void;
  onActivity: (contractId: number) => void;
  onBookVenue: (contract: Contract) => void;
  onLineup: (contract: Contract) => void;
  matchday: MatchdayHandlers;
  onBack: () => void;
}

export function ContractScreen(props: Props) {
  const { controller, onPropose, onActivity, onBookVenue, onLineup, onBack } = props;
  const [reason, setReason] = useState('');
  const busy = controller.action.busy;
  return (
    <Screen title="Contrato del partido" onBack={onBack}>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(contract) => {
          const can = contractActions(contract);
          const amendment = contract.signed !== null && contract.signed.version !== contract.current.version;
          const confirmSign = () =>
            Alert.alert('¿Firmar esta versión?', 'Tu firma compromete a tu equipo con estas condiciones.', [
              { text: 'Revisar', style: 'cancel' },
              { text: 'Firmar', onPress: () => void controller.handleSign(contract.current.version) },
            ]);
          return (
            <>
              <Text style={styles.title}>
                {contract.host.name} (local) vs {contract.guest.name} (visitante)
              </Text>
              <Text style={styles.status} accessibilityLiveRegion="polite">
                {contract.ready_to_play ? 'Listo para jugar. ' : ''}
                {CONTRACT_STATUS_LABEL[contract.status]}. {can.status}
              </Text>
              {contract.referee ? (
                <Text style={styles.line}>
                  Árbitro: {contract.referee.display_name}
                  {contract.referee.status === 'PENDING' ? ' (por aceptar)' : ''}
                </Text>
              ) : null}
              {contract.cancel_reason ? (
                <Text style={styles.line}>Motivo: {contract.cancel_reason}</Text>
              ) : null}
              <VersionCard
                contract={contract}
                version={contract.current}
                title={amendment ? 'Cambio propuesto' : 'Condiciones'}
              />
              {amendment && contract.signed ? (
                <VersionCard contract={contract} version={contract.signed} title="Versión firmada vigente" />
              ) : null}
              <BookingCard
                contract={contract}
                busy={busy}
                onBook={() => onBookVenue(contract)}
                onCancel={(id) => void controller.handleCancelBooking(id)}
              />
              <ResultPanel
                contract={contract}
                canReport={can.canReportResult}
                busy={busy}
                onReport={(h, g) => void controller.handleReport(h, g)}
                onLineup={contract.is_staff ? () => onLineup(contract) : undefined}
              />
              {can.canSign ? <PrimaryButton label="Firmar" disabled={busy} onPress={confirmSign} /> : null}
              {can.canRejectAmendment ? (
                <PrimaryButton
                  label={
                    contract.current.proposed_by_side === contract.my_side
                      ? 'Retirar mi cambio'
                      : 'Rechazar cambio'
                  }
                  variant="secondary"
                  disabled={busy}
                  onPress={() => void controller.handleRejectAmendment(contract.current.version)}
                />
              ) : null}
              {can.canPropose ? (
                <PrimaryButton
                  label="Proponer cambios"
                  variant="secondary"
                  disabled={busy}
                  onPress={() => onPropose(contract)}
                />
              ) : null}
              {can.canCancel ? (
                <>
                  <TextField label="Motivo para cancelar" value={reason} onChangeText={setReason} />
                  <PrimaryButton
                    label="Cancelar partido"
                    variant="danger"
                    disabled={busy || reason.trim().length < 5}
                    onPress={() => void controller.handleCancel(reason)}
                  />
                </>
              ) : null}
              <MatchdayButtons contract={contract} handlers={props.matchday} />
              <PrimaryButton
                label="Ver actividad"
                variant="secondary"
                onPress={() => onActivity(contract.id)}
              />
              <Text style={styles.meta}>
                Sin pagos en la app: árbitro y cancha se pagan por fuera, como lo acuerden.
              </Text>
            </>
          );
        }}
      </StateView>
      {controller.action.message ? (
        <Text style={styles.line} accessibilityLiveRegion="polite">
          {controller.action.message}
        </Text>
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  title: { color: colors.text, fontSize: font.body, fontWeight: '700' },
  status: { color: colors.text, fontSize: font.body },
  line: { color: colors.text, fontSize: font.small },
  meta: { color: colors.textMuted, fontSize: font.small },
});
