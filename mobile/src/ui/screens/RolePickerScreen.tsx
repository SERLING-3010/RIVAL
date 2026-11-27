import { StyleSheet, Text } from 'react-native';

import { ROLE_OPTIONS } from '../../domain/labels';
import type { UserRole } from '../../domain/models';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { colors, font } from '../theme';
import { roleOptions } from '../../domain/features';
import { useFeatures } from '../FeaturesContext';

interface Props {
  onPickRole: (role: UserRole) => void;
  onLogin: () => void;
}

export function RolePickerScreen({ onPickRole, onLogin }: Props) {
  const features = useFeatures(); // Sprint 29: solo jugadores y DT en el lanzamiento
  return (
    <Screen title="Bienvenido a RIVAL">
      <Text style={styles.lead}>
        ¿Cómo quieres registrarte? Luego puedes agregar otro rol desde tu perfil.
      </Text>
      {roleOptions(ROLE_OPTIONS, features).map((option) => (
        <Card
          key={option.role}
          title={option.title}
          subtitle={option.description}
          onPress={() => onPickRole(option.role)}
        />
      ))}
      <PrimaryButton label="Ya tengo cuenta" variant="secondary" onPress={onLogin} />
    </Screen>
  );
}

const styles = StyleSheet.create({
  lead: { color: colors.textMuted, fontSize: font.body },
});
