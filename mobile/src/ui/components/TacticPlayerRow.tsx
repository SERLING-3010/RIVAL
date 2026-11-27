// Un jugador en la alineación: titular (con posición), suplente o fuera.

import { StyleSheet, Text, View } from 'react-native';

import type { Role, TacticSlot } from '../../domain/tacticsModels';
import { colors, font, space } from '../theme';
import { ChoiceChips } from './ChoiceChips';
import { TextField } from './TextField';

const ROLES = [
  { value: 'starter', label: 'Titular' },
  { value: 'sub', label: 'Suplente' },
  { value: 'out', label: 'Fuera' },
];
const ROLE_LABEL: Record<Role, string> = { starter: 'Titular', sub: 'Suplente', out: 'Fuera' };

interface Props {
  player: TacticSlot;
  role: Role;
  position: string;
  editable: boolean;
  onRole: (role: Role) => void;
  onPosition: (text: string) => void;
}

export function TacticPlayerRow({ player, role, position, editable, onRole, onPosition }: Props) {
  const name = player.still_going ? player.display_name : `${player.display_name} (ya no va)`;
  if (!editable) {
    return (
      <Text style={player.still_going ? styles.line : styles.warning}>
        {name} · {role === 'starter' ? position || 'Titular' : ROLE_LABEL[role]}
      </Text>
    );
  }
  return (
    <View style={styles.row}>
      <ChoiceChips label={name} choices={ROLES} selected={[role]} onToggle={(v) => onRole(v as Role)} />
      {role === 'starter' ? (
        <TextField label={`Posición de ${player.display_name}`} value={position} onChangeText={onPosition} />
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  row: { marginBottom: space.sm },
  line: { color: colors.text, fontSize: font.body },
  warning: { color: colors.warning, fontSize: font.body },
});
