import { StyleSheet, Text } from 'react-native';

import type { FormController, RequestForm } from '../../controllers/useMatchForms';
import { PLACE_LABEL, REFEREE_LABEL, SCOPE_LABEL } from '../../domain/matchLabels';
import type { PlaceKind, RefereeMode, SearchScope } from '../../domain/matchModels';
import { ChoiceChips } from '../components/ChoiceChips';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { TextField } from '../components/TextField';
import { colors, font } from '../theme';

interface Props {
  controller: FormController<RequestForm>;
  isChallenge: boolean;
  onBack: () => void;
}

const SCOPES: SearchScope[] = ['NEARBY', 'NEIGHBORHOOD', 'CITY'];
const REFEREES: RefereeMode[] = ['EITHER', 'WITH', 'WITHOUT'];
const PLACES: PlaceKind[] = ['TO_AGREE', 'INFORMAL', 'VENUE'];

export function CreateMatchRequestScreen({ controller, isChallenge, onBack }: Props) {
  const { form, handleChange, action } = controller;
  return (
    <Screen title={isChallenge ? 'Retar equipo' : 'Publicar búsqueda'} onBack={onBack}>
      <TextField
        label="Desde (dd/mm/aaaa hh:mm)"
        value={form.start}
        onChangeText={(v) => handleChange('start', v)}
      />
      <TextField
        label="Hasta (dd/mm/aaaa hh:mm)"
        value={form.end}
        onChangeText={(v) => handleChange('end', v)}
      />
      {!isChallenge ? (
        <ChoiceChips
          label="¿Quién puede verla?"
          selected={[form.scope]}
          choices={SCOPES.map((s) => ({ value: s, label: SCOPE_LABEL[s] }))}
          onToggle={(v) => handleChange('scope', v as SearchScope)}
        />
      ) : null}
      <ChoiceChips
        label="Árbitro"
        selected={[form.referee]}
        choices={REFEREES.map((r) => ({ value: r, label: REFEREE_LABEL[r] }))}
        onToggle={(v) => handleChange('referee', v as RefereeMode)}
      />
      <ChoiceChips
        label="Lugar"
        selected={[form.place]}
        choices={PLACES.map((p) => ({ value: p, label: PLACE_LABEL[p] }))}
        onToggle={(v) => handleChange('place', v as PlaceKind)}
      />
      <TextField
        label="Detalle del lugar (opcional)"
        value={form.placeNote}
        hint="Ej.: Parque del barrio, cancha de arena. Los pagos se acuerdan por fuera de la app."
        onChangeText={(v) => handleChange('placeNote', v)}
      />
      <TextField
        label="Mensaje (opcional)"
        value={form.message}
        onChangeText={(v) => handleChange('message', v)}
      />
      {controller.error ? <Text style={styles.error}>{controller.error}</Text> : null}
      {action.message ? (
        <Text style={styles.message} accessibilityLiveRegion="polite">
          {action.message}
        </Text>
      ) : null}
      <PrimaryButton
        label={isChallenge ? 'Enviar reto' : 'Publicar'}
        loading={action.busy}
        onPress={() => void controller.handleSubmit()}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  error: { color: colors.danger, fontSize: font.body },
  message: { color: colors.text, fontSize: font.body },
});
