import { StyleSheet, Switch, Text, View } from 'react-native';

import type { CreateTeamController } from '../../controllers/useCreateTeamForm';
import type { Sport } from '../../domain/models';
import { ChoiceChips } from '../components/ChoiceChips';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { TextField } from '../components/TextField';
import { colors, font, space } from '../theme';

interface Props {
  controller: CreateTeamController;
  sports: Sport[];
  isCoach: boolean;
  onBack: () => void;
}

export function CreateTeamScreen({ controller, sports, isCoach, onBack }: Props) {
  const { form, errors } = controller;
  const modalities = sports.find((s) => s.code === form.sport)?.modalities ?? [];
  return (
    <Screen title="Crear equipo" onBack={onBack}>
      <TextField
        label="Nombre del equipo"
        value={form.name}
        error={errors.name}
        onChangeText={(v) => controller.handleText('name', v)}
      />
      <ChoiceChips
        label="Deporte"
        selected={form.sport ? [form.sport] : []}
        error={errors.sport}
        choices={sports.map((s) => ({ value: s.code, label: s.name }))}
        onToggle={controller.handleSport}
      />
      {modalities.length > 0 ? (
        <ChoiceChips
          label="Modalidad"
          selected={form.modality ? [form.modality] : []}
          error={errors.modality}
          choices={modalities.map((m) => ({ value: m.code, label: m.name }))}
          onToggle={controller.handleModality}
        />
      ) : null}
      <TextField
        label="Ciudad"
        value={form.city}
        error={errors.city}
        onChangeText={(v) => controller.handleText('city', v)}
      />
      <TextField
        label="Barrio donde juegan"
        value={form.neighborhood}
        error={errors.neighborhood}
        hint="Los rivales verán el barrio, nunca una ubicación exacta."
        onChangeText={(v) => controller.handleText('neighborhood', v)}
      />
      {isCoach ? (
        <View style={styles.switchRow}>
          <Text style={styles.switchLabel}>Entrar como DT (si no, entras como capitán)</Text>
          <Switch
            value={form.asCoach}
            onValueChange={controller.handleAsCoach}
            accessibilityLabel="Entrar como director técnico"
          />
        </View>
      ) : (
        <Text style={styles.note}>
          Entrarás como capitán y administrarás el equipo hasta que llegue un DT.
        </Text>
      )}
      {controller.submitError ? (
        <Text style={styles.error} accessibilityLiveRegion="assertive">
          {controller.submitError}
        </Text>
      ) : null}
      <PrimaryButton
        label="Crear equipo"
        loading={controller.submitting}
        onPress={() => void controller.handleSubmit()}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  switchRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: space.md },
  switchLabel: { flex: 1, color: colors.text, fontSize: font.body },
  note: { color: colors.textMuted, fontSize: font.small },
  error: { color: colors.danger, fontSize: font.body },
});
