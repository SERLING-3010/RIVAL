// Planilla del partido: marcar quién jugó, los goles de cada uno y su tipo (Sprint 23).

import { StyleSheet, Text } from 'react-native';

import type { LineupController } from '../../controllers/useLineup';
import type { SquadMember } from '../../domain/managerModels';
import type { ViewState } from '../../domain/viewState';
import { Card } from '../components/Card';
import { ChoiceChips } from '../components/ChoiceChips';
import { GoalKindPicker } from '../components/GoalKindPicker';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { TextField } from '../components/TextField';
import { colors, font } from '../theme';

interface Props {
  controller: LineupController;
  squad: ViewState<SquadMember[]>;
  teamScore: number;
  onRetry: () => void;
  onBack: () => void;
}

export function LineupScreen({ controller, squad, teamScore, onRetry, onBack }: Props) {
  const { played, goals, kinds, action } = controller;
  return (
    <Screen title="Planilla del partido" onBack={onBack}>
      <Text style={styles.meta}>
        Tu equipo hizo {teamScore} gol(es). Marca quién jugó; la suma de goles no puede superar el marcador.
      </Text>
      <StateView state={squad} onRetry={onRetry}>
        {(members) => (
          <>
            <ChoiceChips
              label="Jugaron"
              selected={played.map(String)}
              choices={members.map((m) => ({ value: String(m.user_id), label: m.display_name }))}
              onToggle={(v) => controller.handleToggle(Number(v))}
            />
            {members
              .filter((m) => played.includes(m.user_id))
              .map((m) => (
                <Card key={m.user_id} title={m.display_name}>
                  <TextField
                    label={`Goles de ${m.display_name}`}
                    keyboardType="number-pad"
                    value={goals[m.user_id] ?? ''}
                    placeholder="0"
                    onChangeText={(v) => controller.handleGoals(m.user_id, v)}
                  />
                  <GoalKindPicker
                    name={m.display_name}
                    goals={Number(goals[m.user_id] ?? '') || 0}
                    marked={kinds[m.user_id] ?? []}
                    onAdd={(kind) => controller.handleAddKind(m.user_id, kind)}
                    onRemove={(i) => controller.handleRemoveKind(m.user_id, i)}
                  />
                </Card>
              ))}
          </>
        )}
      </StateView>
      {controller.error ? <Text style={styles.error}>{controller.error}</Text> : null}
      {action.message ? (
        <Text style={styles.message} accessibilityLiveRegion="polite">
          {action.message}
        </Text>
      ) : null}
      <PrimaryButton
        label="Guardar planilla"
        loading={action.busy}
        onPress={() => void controller.handleSubmit()}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  meta: { color: colors.textMuted, fontSize: font.small },
  error: { color: colors.danger, fontSize: font.body },
  message: { color: colors.text, fontSize: font.body },
});
