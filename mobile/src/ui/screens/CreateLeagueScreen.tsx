import { StyleSheet, Text } from 'react-native';

import type { CreateLeagueController } from '../../controllers/useCreateLeague';
import type { Sport } from '../../domain/models';
import { ChoiceChips } from '../components/ChoiceChips';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { TextField } from '../components/TextField';
import { colors, font } from '../theme';

interface Props {
  controller: CreateLeagueController;
  sports: Sport[];
  onBack: () => void;
}

export function CreateLeagueScreen({ controller, sports, onBack }: Props) {
  const { form, handleChange, action } = controller;
  const modalities = sports.find((s) => s.code === form.sport)?.modalities ?? [];
  return (
    <Screen title="Crear liga" onBack={onBack}>
      <Text style={styles.meta}>Quedas como organizador. Después puedes nombrar coorganizadores.</Text>
      <TextField label="Nombre de la liga" value={form.name} onChangeText={(v) => handleChange('name', v)} />
      <ChoiceChips
        label="Deporte"
        selected={form.sport ? [form.sport] : []}
        choices={sports.map((s) => ({ value: s.code, label: s.name }))}
        onToggle={(v) => handleChange('sport', v)}
      />
      {modalities.length > 0 ? (
        <ChoiceChips
          label="Modalidad"
          selected={form.modality ? [form.modality] : []}
          choices={modalities.map((m) => ({ value: m.code, label: m.name }))}
          onToggle={(v) => handleChange('modality', v)}
        />
      ) : null}
      <TextField label="Ciudad" value={form.city} onChangeText={(v) => handleChange('city', v)} />
      <TextField
        label="Temporada"
        hint="Por ejemplo 2026, 2026-1 o 2026-2"
        value={form.season}
        onChangeText={(v) => handleChange('season', v)}
      />
      <TextField
        label="Descripción (opcional)"
        value={form.description}
        onChangeText={(v) => handleChange('description', v)}
      />
      {controller.error ? <Text style={styles.error}>{controller.error}</Text> : null}
      {action.message ? (
        <Text style={styles.message} accessibilityLiveRegion="polite">
          {action.message}
        </Text>
      ) : null}
      <PrimaryButton
        label="Crear liga"
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
