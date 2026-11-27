import { StyleSheet, Text } from 'react-native';

import type { Loader } from '../../controllers/useLoader';
import type { ContractSummary } from '../../domain/contractModels';
import { CONTRACT_STATUS_LABEL, RESULT_STATUS_LABEL } from '../../domain/contractRules';
import { formatLocal } from '../../domain/dateTime';
import { Card } from '../components/Card';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { colors, font } from '../theme';

interface Props {
  controller: Loader<ContractSummary[]>;
  onOpen: (contractId: number) => void;
  onBack: () => void;
}

export function ContractsScreen({ controller, onOpen, onBack }: Props) {
  return (
    <Screen title="Partidos pactados" onBack={onBack}>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(items) =>
          items.map((item) => (
            <Card
              key={item.id}
              title={
                item.result_status === 'CONFIRMED'
                  ? `${item.host.name} ${item.host_score} – ${item.guest_score} ${item.guest.name}`
                  : `${item.host.name} vs ${item.guest.name}`
              }
              subtitle={formatLocal(item.kickoff_at)}
              badge={
                item.result_status
                  ? RESULT_STATUS_LABEL[item.result_status]
                  : CONTRACT_STATUS_LABEL[item.status]
              }
              onPress={() => onOpen(item.id)}
            >
              {item.awaiting_my_signature ? (
                <Text style={styles.alert}>Falta la firma de tu equipo</Text>
              ) : null}
            </Card>
          ))
        }
      </StateView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  alert: { color: colors.text, fontSize: font.small, fontWeight: '700' },
});
