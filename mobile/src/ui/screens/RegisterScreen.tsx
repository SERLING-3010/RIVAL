import { StyleSheet, Text } from 'react-native';

import type { RegistrationController } from '../../controllers/useRegistrationForm';
import { roleTitle } from '../../domain/labels';
import type { Sport } from '../../domain/models';
import type { ViewState } from '../../domain/viewState';
import { ChoiceChips } from '../components/ChoiceChips';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { TextField } from '../components/TextField';
import { colors, font } from '../theme';

interface Props {
  controller: RegistrationController;
  catalog: ViewState<Sport[]>;
  onRetryCatalog: () => void;
  onBack: () => void;
}

export function RegisterScreen({ controller, catalog, onRetryCatalog, onBack }: Props) {
  const { form, errors } = controller;
  const plays = form.role === 'PLAYER' || form.role === 'COACH';
  return (
    <Screen title={`Registro: ${roleTitle(form.role)}`} onBack={onBack}>
      <TextField
        label="Nombre visible"
        value={form.displayName}
        error={errors.displayName}
        onChangeText={(v) => controller.handleChange('displayName', v)}
      />
      <TextField
        label="Correo"
        value={form.email}
        error={errors.email}
        keyboardType="email-address"
        onChangeText={(v) => controller.handleChange('email', v)}
      />
      <TextField
        label="Contraseña"
        value={form.password}
        error={errors.password}
        secure
        hint="Mínimo 10 caracteres. Puedes pegarla desde tu gestor de contraseñas."
        onChangeText={(v) => controller.handleChange('password', v)}
      />
      <TextField
        label="Fecha de nacimiento"
        value={form.birthDate}
        error={errors.birthDate}
        placeholder="dd/mm/aaaa"
        keyboardType="numbers-and-punctuation"
        hint="RIVAL es solo para mayores de 18 años."
        onChangeText={(v) => controller.handleChange('birthDate', v)}
      />
      <StateView state={catalog} onRetry={onRetryCatalog}>
        {(sports) => (
          <ChoiceChips
            label="¿Para qué deportes?"
            selected={form.sports}
            error={errors.sports}
            choices={sports.map((s) => ({ value: s.code, label: s.name }))}
            onToggle={controller.handleToggleSport}
          />
        )}
      </StateView>
      <TextField
        label="Ciudad"
        value={form.city}
        error={errors.city}
        onChangeText={(v) => controller.handleChange('city', v)}
      />
      <TextField
        label="Barrio"
        value={form.neighborhood}
        error={errors.neighborhood}
        hint="Solo se muestra tu barrio, nunca tu ubicación exacta."
        onChangeText={(v) => controller.handleChange('neighborhood', v)}
      />
      {plays ? (
        <TextField
          label="Posición (opcional)"
          value={form.position}
          onChangeText={(v) => controller.handleChange('position', v)}
        />
      ) : null}
      {controller.submitError ? (
        <Text style={styles.error} accessibilityLiveRegion="assertive">
          {controller.submitError}
        </Text>
      ) : null}
      <PrimaryButton
        label="Crear cuenta"
        loading={controller.submitting}
        onPress={() => void controller.handleSubmit()}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  error: { color: colors.danger, fontSize: font.body },
});
