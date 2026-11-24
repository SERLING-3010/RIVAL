import { StyleSheet, Switch, Text, View } from 'react-native';

import type { FreeAgentPanelController } from '../../controllers/useFreeAgentPanel';
import type { Sport } from '../../domain/models';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { colors, font, space } from '../theme';

interface Props {
  controller: FreeAgentPanelController;
  sports: Sport[];
  mySports: string[];
  onBack: () => void;
}

export function FreeAgentPanelScreen({ controller, sports, mySports, onBack }: Props) {
  const { action } = controller;
  return (
    <Screen title="Agente libre" onBack={onBack}>
      <Text style={styles.note}>
        Los DT de tu ciudad podrán encontrarte e invitarte. Solo verán tu nombre visible, posición y barrio.
      </Text>
      <StateView state={controller.profiles.state} onRetry={controller.profiles.handleReload}>
        {(profiles) =>
          mySports.map((code) => {
            const current = profiles.find((p) => p.sport_code === code);
            const name = sports.find((s) => s.code === code)?.name ?? code;
            return (
              <View key={code} style={styles.row}>
                <Text style={styles.label}>Disponible en {name}</Text>
                <Switch
                  value={current?.active ?? false}
                  disabled={action.busy}
                  onValueChange={(value) => void controller.handleToggle(code, value, current)}
                  accessibilityLabel={`Aparecer como agente libre en ${name}`}
                />
              </View>
            );
          })
        }
      </StateView>
      <Text style={styles.section} accessibilityRole="header">
        Invitaciones de equipos
      </Text>
      <StateView state={controller.invitations.state} onRetry={controller.invitations.handleReload}>
        {(items) =>
          items.map((invitation) => (
            <Card
              key={invitation.id}
              title={invitation.team.name}
              subtitle={`${invitation.team.modality_code} · ${invitation.team.neighborhood}, ${invitation.team.city}`}
            >
              {invitation.message ? <Text style={styles.label}>“{invitation.message}”</Text> : null}
              <PrimaryButton
                label="Aceptar"
                disabled={action.busy}
                onPress={() => void controller.handleRespond(invitation.id, true)}
              />
              <PrimaryButton
                label="Rechazar"
                variant="secondary"
                disabled={action.busy}
                onPress={() => void controller.handleRespond(invitation.id, false)}
              />
            </Card>
          ))
        }
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
  note: { color: colors.textMuted, fontSize: font.small },
  row: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: space.md },
  label: { flex: 1, color: colors.text, fontSize: font.body },
  section: { color: colors.text, fontSize: font.heading, fontWeight: '700' },
});
