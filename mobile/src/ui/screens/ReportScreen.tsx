// Reportar a una persona o a un equipo. No sanciona a nadie por sí solo: lo revisa una persona.

import { StyleSheet, Text } from 'react-native';

import type { ReportController } from '../../controllers/useReport';
import type { ReportCategory } from '../../domain/moderationModels';
import { CATEGORY_LABEL } from '../../domain/moderationModels';
import { ChoiceChips } from '../components/ChoiceChips';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { TextField } from '../components/TextField';
import { colors, font } from '../theme';

interface Props {
  controller: ReportController;
  targetName: string;
  onBack: () => void;
}

const CATEGORIES: ReportCategory[] = ['AGGRESSION', 'NO_SHOW', 'FAKE_PROFILE', 'OTHER'];

export function ReportScreen({ controller, targetName, onBack }: Props) {
  return (
    <Screen title={`Reportar a ${targetName}`} onBack={onBack}>
      <Text style={styles.meta}>
        Una persona moderadora revisará el reporte. Nunca hay sanciones automáticas.
      </Text>
      <ChoiceChips
        label="Motivo"
        selected={[controller.category]}
        choices={CATEGORIES.map((c) => ({ value: c, label: CATEGORY_LABEL[c] }))}
        onToggle={(v) => controller.handleCategory(v as ReportCategory)}
      />
      <TextField
        label="Qué pasó (10 a 500 caracteres)"
        value={controller.description}
        onChangeText={controller.handleDescription}
        error={controller.error ?? undefined}
      />
      {controller.action.message ? (
        <Text style={styles.message} accessibilityLiveRegion="polite">
          {controller.action.message}
        </Text>
      ) : null}
      <PrimaryButton
        label="Enviar reporte"
        loading={controller.action.busy}
        onPress={() => void controller.handleSubmit()}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  meta: { color: colors.textMuted, fontSize: font.small },
  message: { color: colors.text, fontSize: font.body },
});
