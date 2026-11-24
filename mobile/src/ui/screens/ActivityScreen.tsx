import { StyleSheet, Text } from 'react-native';

import type { Loader } from '../../controllers/useLoader';
import type { ActivityItem } from '../../domain/activityLabels';
import { actionLabel, actorText, changeLines } from '../../domain/activityLabels';
import { formatLocal } from '../../domain/dateTime';
import { Card } from '../components/Card';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { colors, font } from '../theme';

interface Props {
  title: string;
  controller: Loader<ActivityItem[]>;
  onBack: () => void;
}

export function ActivityScreen({ title, controller, onBack }: Props) {
  return (
    <Screen title={title} onBack={onBack}>
      <Text style={styles.meta}>Quién hizo cada cambio, del más reciente al más antiguo.</Text>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(items) =>
          items.map((item, index) => (
            <Card
              key={`${item.occurred_at}-${item.action}-${index}`}
              title={actionLabel(item.action)}
              subtitle={`${actorText(item)} · ${formatLocal(item.occurred_at)}`}
            >
              {item.approver_name ? <Text style={styles.meta}>Aprobó: {item.approver_name}</Text> : null}
              {changeLines(item).map((line) => (
                <Text key={line} style={styles.line}>
                  {line}
                </Text>
              ))}
            </Card>
          ))
        }
      </StateView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  line: { color: colors.text, fontSize: font.small },
  meta: { color: colors.textMuted, fontSize: font.small },
});
