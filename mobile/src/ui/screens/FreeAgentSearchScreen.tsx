import { StyleSheet, Switch, Text, View } from 'react-native';

import type { FreeAgentSearchController } from '../../controllers/useScouting';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { LoadMore } from '../components/LoadMore';
import { StateView } from '../components/StateView';
import { colors, font, space } from '../theme';

interface Props {
  controller: FreeAgentSearchController;
  onBack: () => void;
}

export function FreeAgentSearchScreen({ controller, onBack }: Props) {
  const { action } = controller;
  return (
    <Screen title="Agentes libres" onBack={onBack}>
      <View style={styles.row}>
        <Text style={styles.label}>Solo de mi barrio</Text>
        <Switch
          value={controller.onlyMyNeighborhood}
          onValueChange={controller.handleOnlyNeighborhood}
          accessibilityLabel="Mostrar solo agentes libres de mi barrio"
        />
      </View>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(page) => (
          <>
            {page.items.map((agent) => (
              <Card
                key={agent.user_id}
                title={agent.display_name}
                subtitle={`${agent.position ?? 'Sin posición'} · ${agent.neighborhood}, ${agent.city}`}
              >
                {agent.note ? <Text style={styles.label}>{agent.note}</Text> : null}
                {controller.invited[agent.user_id] ? (
                  <Text style={styles.done}>Invitación enviada</Text>
                ) : (
                  <PrimaryButton
                    label="Invitar al equipo"
                    disabled={action.busy}
                    onPress={() => void controller.handleInvite(agent.user_id)}
                  />
                )}
              </Card>
            ))}
            <LoadMore
              hasMore={controller.hasMore}
              loading={controller.loadingMore}
              error={controller.moreError}
              onPress={() => void controller.handleLoadMore()}
            />
          </>
        )}
      </StateView>
      {action.message ? (
        <Text style={styles.label} accessibilityLiveRegion="polite">
          {action.message}
        </Text>
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: space.md },
  label: { flex: 1, color: colors.text, fontSize: font.body },
  done: { color: colors.success, fontSize: font.small, fontWeight: '600' },
});
