import { StyleSheet, Text } from 'react-native';

import type { LoginController } from '../../controllers/useLoginForm';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { TextField } from '../components/TextField';
import { colors, font } from '../theme';

interface Props {
  controller: LoginController;
  onBack: () => void;
}

export function LoginScreen({ controller, onBack }: Props) {
  return (
    <Screen title="Iniciar sesión" onBack={onBack}>
      <TextField
        label="Correo"
        value={controller.email}
        keyboardType="email-address"
        onChangeText={controller.handleEmail}
      />
      <TextField
        label="Contraseña"
        value={controller.password}
        secure
        onChangeText={controller.handlePassword}
      />
      {controller.error ? (
        <Text style={styles.error} accessibilityLiveRegion="assertive">
          {controller.error}
        </Text>
      ) : null}
      <PrimaryButton
        label="Entrar"
        loading={controller.submitting}
        onPress={() => void controller.handleSubmit()}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  error: { color: colors.danger, fontSize: font.body },
});
