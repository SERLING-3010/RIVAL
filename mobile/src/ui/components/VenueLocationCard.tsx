// El dueño guarda la ubicación de su establecimiento, parado en él, para que funcione el check-in.

import { StyleSheet, Text } from 'react-native';

import type { VenueLocationController } from '../../controllers/useCheckIn';
import { colors, font } from '../theme';
import { Card } from './Card';
import { PrimaryButton } from './PrimaryButton';

interface Props {
  hasLocation: boolean;
  controller: VenueLocationController;
}

export function VenueLocationCard({ hasLocation, controller }: Props) {
  return (
    <Card
      title="Ubicación para el check-in"
      badge={hasLocation ? 'Guardada' : 'Falta'}
      subtitle="Hazlo estando en la cancha. Es la ubicación del negocio, no la tuya: los jugadores no la ven."
    >
      <PrimaryButton
        label={hasLocation ? 'Actualizar: estoy en la cancha' : 'Guardar: estoy en la cancha'}
        variant={hasLocation ? 'secondary' : 'primary'}
        disabled={controller.action.busy}
        onPress={() => void controller.handleSaveHere()}
      />
      {controller.action.message ? (
        <Text style={styles.meta} accessibilityLiveRegion="polite">
          {controller.action.message}
        </Text>
      ) : null}
    </Card>
  );
}

const styles = StyleSheet.create({
  meta: { color: colors.textMuted, fontSize: font.small },
});
