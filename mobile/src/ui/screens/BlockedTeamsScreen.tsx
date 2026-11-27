// Equipos bloqueados por mi equipo: mientras dure, ninguno ve al otro ni puede retarlo.

import { StyleSheet, Text } from 'react-native';

import type { BlocksController } from '../../controllers/useModeration';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { colors, font } from '../theme';

interface Props {
  controller: BlocksController;
  onBack: () => void;
}

export function BlockedTeamsScreen({ controller, onBack }: Props) {
  return (
    <Screen title="Equipos bloqueados" onBack={onBack}>
      <Text style={styles.meta}>Un equipo bloqueado no ve al tuyo, ni puede retarlo ni ofertarle.</Text>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(items) =>
          items.map((b) => (
            <Card key={b.team.id} title={b.team.name} subtitle={`${b.team.neighborhood}, ${b.team.city}`}>
              <PrimaryButton
                label="Desbloquear"
                variant="secondary"
                disabled={controller.action.busy}
                onPress={() => void controller.handleUnblock(b.team.id)}
              />
            </Card>
          ))
        }
      </StateView>
      {controller.action.message ? (
        <Text style={styles.meta} accessibilityLiveRegion="polite">
          {controller.action.message}
        </Text>
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  meta: { color: colors.textMuted, fontSize: font.small },
});
