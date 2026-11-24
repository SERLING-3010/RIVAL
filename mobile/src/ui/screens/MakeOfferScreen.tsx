import { StyleSheet, Text } from 'react-native';

import type { FormController, OfferForm } from '../../controllers/useMatchForms';
import { formatLocal } from '../../domain/dateTime';
import { PLACE_LABEL, REFEREE_LABEL } from '../../domain/matchLabels';
import type { MatchRequest, PlaceKind } from '../../domain/matchModels';
import { ChoiceChips } from '../components/ChoiceChips';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { TextField } from '../components/TextField';
import { colors, font } from '../theme';

interface Props {
  controller: FormController<OfferForm>;
  request: MatchRequest;
  onBack: () => void;
}

const PLACES: PlaceKind[] = ['TO_AGREE', 'INFORMAL', 'VENUE'];

export function MakeOfferScreen({ controller, request, onBack }: Props) {
  const { form, handleChange, action } = controller;
  const refereeChoices: OfferForm['referee'][] =
    request.referee_mode === 'EITHER' ? ['WITHOUT', 'WITH'] : [request.referee_mode];
  return (
    <Screen title={`Oferta a ${request.team.name}`} onBack={onBack}>
      <Text style={styles.meta}>
        Juegan entre {formatLocal(request.window_start)} y {formatLocal(request.window_end)}.
      </Text>
      <TextField
        label="Fecha y hora propuesta (dd/mm/aaaa hh:mm)"
        value={form.start}
        onChangeText={(v) => handleChange('start', v)}
      />
      <ChoiceChips
        label="Árbitro"
        selected={[form.referee]}
        choices={refereeChoices.map((r) => ({ value: r, label: REFEREE_LABEL[r] }))}
        onToggle={(v) => handleChange('referee', v as OfferForm['referee'])}
      />
      <ChoiceChips
        label="Lugar"
        selected={[form.place]}
        choices={PLACES.map((p) => ({ value: p, label: PLACE_LABEL[p] }))}
        onToggle={(v) => handleChange('place', v as PlaceKind)}
      />
      <TextField
        label="Detalle del lugar"
        value={form.placeNote}
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
        label="Enviar oferta"
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
