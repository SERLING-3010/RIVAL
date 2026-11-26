// Mi cuenta (Sprint 27, Ley 1581): textos legales, descargar mis datos, eliminar la cuenta y cerrar sesión.

import { Alert, StyleSheet, Text } from 'react-native';

import type { MyDataController } from '../../controllers/useMyData';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { TextField } from '../components/TextField';
import { colors, font } from '../theme';

interface Props {
  controller: MyDataController;
  onOpenLegal: (doc: 'terms' | 'privacy') => void;
  onBack: () => void;
  onLogout: () => void;
}

export function MyDataScreen({ controller, onOpenLegal, onBack, onLogout }: Props) {
  const confirmDelete = () =>
    Alert.alert(
      '¿Eliminar tu cuenta?',
      'Se borran tu correo, nombre, fecha de nacimiento, barrio, sesiones y mensajes. Tus partidos quedan ' +
        'como de un «Jugador eliminado». No se puede deshacer.',
      [
        { text: 'No, volver', style: 'cancel' },
        { text: 'Eliminar mi cuenta', style: 'destructive', onPress: () => void controller.handleDelete() },
      ],
    );
  return (
    <Screen title="Mis datos y privacidad" onBack={onBack}>
      <Card title="Textos legales">
        <PrimaryButton label="Términos de uso" variant="secondary" onPress={() => onOpenLegal('terms')} />
        <PrimaryButton
          label="Política de privacidad"
          variant="secondary"
          onPress={() => onOpenLegal('privacy')}
        />
      </Card>
      <Card title="Descargar mis datos">
        <Text style={styles.meta}>
          Todo lo que RIVAL guarda de ti: perfil, equipos, partidos, valoraciones recibidas, mensajes y
          check-ins. Nunca guardamos tu ubicación exacta.
        </Text>
        <PrimaryButton
          label="Descargar mis datos"
          loading={controller.action.busy}
          onPress={() => void controller.handleExport()}
        />
        {controller.action.message ? (
          <Text style={styles.meta} accessibilityLiveRegion="polite">
            {controller.action.message}
          </Text>
        ) : null}
      </Card>
      <Card title="Eliminar mi cuenta">
        <Text style={styles.meta}>
          Antes sal de tus equipos y entrega tus ligas o canchas, para que nadie quede sin responsable.
        </Text>
        <TextField
          label="Tu contraseña"
          value={controller.password}
          secure
          onChangeText={controller.handlePassword}
        />
        {controller.error ? (
          <Text style={styles.error} accessibilityLiveRegion="assertive">
            {controller.error}
          </Text>
        ) : null}
        <PrimaryButton label="Eliminar mi cuenta" variant="danger" onPress={confirmDelete} />
      </Card>
      <PrimaryButton label="Cerrar sesión" variant="secondary" onPress={onLogout} />
    </Screen>
  );
}

const styles = StyleSheet.create({
  meta: { color: colors.textMuted, fontSize: font.small },
  error: { color: colors.danger, fontSize: font.body },
});
