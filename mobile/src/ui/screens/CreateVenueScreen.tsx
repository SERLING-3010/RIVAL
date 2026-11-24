import { StyleSheet, Text } from 'react-native';

import type { CreateVenueController } from '../../controllers/useCreateVenue';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { TextField } from '../components/TextField';
import { colors, font } from '../theme';

interface Props {
  controller: CreateVenueController;
  onBack: () => void;
}

export function CreateVenueScreen({ controller, onBack }: Props) {
  const { form, handleChange, action } = controller;
  return (
    <Screen title="Registrar establecimiento" onBack={onBack}>
      <Text style={styles.meta}>
        La dirección del establecimiento es pública. Los pagos se hacen en el establecimiento, fuera de la
        app.
      </Text>
      <TextField label="Nombre" value={form.name} onChangeText={(v) => handleChange('name', v)} />
      <TextField label="Dirección" value={form.address} onChangeText={(v) => handleChange('address', v)} />
      <TextField
        label="Barrio"
        value={form.neighborhood}
        onChangeText={(v) => handleChange('neighborhood', v)}
      />
      <TextField label="Ciudad" value={form.city} onChangeText={(v) => handleChange('city', v)} />
      <TextField
        label="Tarifa de referencia por hora (opcional)"
        hint="En pesos, por ejemplo 80000"
        keyboardType="number-pad"
        value={form.price}
        onChangeText={(v) => handleChange('price', v)}
      />
      {controller.error ? <Text style={styles.error}>{controller.error}</Text> : null}
      {action.message ? (
        <Text style={styles.message} accessibilityLiveRegion="polite">
          {action.message}
        </Text>
      ) : null}
      <PrimaryButton label="Registrar" loading={action.busy} onPress={() => void controller.handleSubmit()} />
    </Screen>
  );
}

const styles = StyleSheet.create({
  meta: { color: colors.textMuted, fontSize: font.small },
  error: { color: colors.danger, fontSize: font.body },
  message: { color: colors.text, fontSize: font.body },
});
