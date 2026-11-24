import { useState } from 'react';
import { Alert, StyleSheet, Text } from 'react-native';

import type { ContractController } from '../../controllers/useContracts';
import type { Contract, ContractVersion } from '../../domain/contractModels';
import { CONTRACT_STATUS_LABEL, contractActions, describeTerms } from '../../domain/contractRules';
import { formatLocal } from '../../domain/dateTime';
import { PLACE_LABEL, REFEREE_LABEL } from '../../domain/matchLabels';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { TextField } from '../components/TextField';
import { colors, font } from '../theme';

interface Props {
  controller: ContractController;
  onPropose: (contract: Contract) => void;
  onBack: () => void;
}

const SIDE_NAME = (c: Contract, side: string) => (side === 'HOST' ? c.host.name : c.guest.name);

function VersionCard({
  contract,
  version,
  title,
}: {
  contract: Contract;
  version: ContractVersion;
  title: string;
}) {
  const t = version.terms;
  const signatures = version.signed_by.map((s) => SIDE_NAME(contract, s)).join(' y ') || 'nadie';
  return (
    <Card title={`${title} · v${version.version}`} subtitle={formatLocal(t.kickoff_at)}>
      <Text style={styles.line}>
        {REFEREE_LABEL[t.referee_mode]} · {PLACE_LABEL[t.place_kind]}
      </Text>
      {t.place_note ? <Text style={styles.line}>Lugar: {t.place_note}</Text> : null}
      {describeTerms(t, contract.host.name, contract.guest.name).map((line) => (
        <Text key={line} style={styles.line}>
          {line}
        </Text>
      ))}
      {version.note ? <Text style={styles.meta}>“{version.note}”</Text> : null}
      <Text style={styles.meta}>Firmada por: {signatures}</Text>
    </Card>
  );
}

export function ContractScreen({ controller, onPropose, onBack }: Props) {
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
                {CONTRACT_STATUS_LABEL[contract.status]}. {can.status}
              </Text>
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
