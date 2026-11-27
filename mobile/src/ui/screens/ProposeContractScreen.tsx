import { StyleSheet, Text } from 'react-native';

import type { ProposalController } from '../../controllers/useContracts';
import type { ContractForm } from '../../domain/contractForm';
import type { CostSplit } from '../../domain/contractModels';
import { COST_SPLIT_LABEL } from '../../domain/contractRules';
import { PLACE_LABEL, REFEREE_LABEL } from '../../domain/matchLabels';
import type { PlaceKind } from '../../domain/matchModels';
import { placeChoices, refereeChoices } from '../../domain/features';
import { ChoiceChips } from '../components/ChoiceChips';
import { useFeatures } from '../FeaturesContext';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { TextField } from '../components/TextField';
import { colors, font } from '../theme';

interface Props {
  controller: ProposalController;
  hostName: string;
  guestName: string;
  onBack: () => void;
}

const SPLITS: CostSplit[] = ['HALF', 'HOST', 'GUEST'];
const PLACES: PlaceKind[] = ['TO_AGREE', 'INFORMAL', 'VENUE'];
const REFEREES: ContractForm['referee'][] = ['WITHOUT', 'WITH'];

export function ProposeContractScreen({ controller, hostName, guestName, onBack }: Props) {
  const { form, handleChange, action } = controller;
  const features = useFeatures(); // Sprint 29
  const referees = refereeChoices(REFEREES, features);
  const splitChoices = SPLITS.map((s) => ({ value: s, label: COST_SPLIT_LABEL[s] }));
  return (
    <Screen title="Proponer cambios" onBack={onBack}>
      <Text style={styles.meta}>
        Al enviar, tu equipo firma la propuesta. El rival debe firmarla para que valga.
      </Text>
      <TextField
        label="Fecha y hora (dd/mm/aaaa hh:mm)"
        value={form.kickoff}
        onChangeText={(v) => handleChange('kickoff', v)}
      />
      <TextField
        label="Duración (minutos)"
        keyboardType="number-pad"
        value={form.duration}
        onChangeText={(v) => handleChange('duration', v)}
      />
      {referees.length > 1 ? (
        <ChoiceChips
          label="Árbitro"
          selected={[form.referee]}
          choices={referees.map((r) => ({ value: r, label: REFEREE_LABEL[r] }))}
          onToggle={(v) => handleChange('referee', v as ContractForm['referee'])}
        />
      ) : null}
      <ChoiceChips
        label="Lugar"
        selected={[form.place]}
        choices={placeChoices(PLACES, features).map((p) => ({ value: p, label: PLACE_LABEL[p] }))}
        onToggle={(v) => handleChange('place', v as PlaceKind)}
      />
      <TextField
        label="Detalle del lugar"
        value={form.placeNote}
        onChangeText={(v) => handleChange('placeNote', v)}
      />
      <TextField
        label={`Uniforme de ${hostName}`}
        value={form.hostKit}
        onChangeText={(v) => handleChange('hostKit', v)}
      />
      <TextField
        label={`Uniforme de ${guestName}`}
        value={form.guestKit}
        onChangeText={(v) => handleChange('guestKit', v)}
      />
      <TextField
        label="Cambios permitidos"
        hint="Vacío = ilimitados"
        keyboardType="number-pad"
        value={form.substitutions}
        onChangeText={(v) => handleChange('substitutions', v)}
      />
      <ChoiceChips
        label="¿Quién paga la cancha?"
        selected={[form.fieldCost]}
        choices={splitChoices}
        onToggle={(v) => handleChange('fieldCost', v as CostSplit)}
      />
      {form.referee === 'WITH' ? (
        <ChoiceChips
          label="¿Quién paga el árbitro?"
          selected={[form.refereeCost]}
          choices={splitChoices}
          onToggle={(v) => handleChange('refereeCost', v as CostSplit)}
        />
      ) : (
        <TextField
          label="¿Quién cobra las faltas dudosas? (opcional)"
          value={form.foulCaller}
          onChangeText={(v) => handleChange('foulCaller', v)}
        />
      )}
      <TextField
        label="Aviso para cancelar (horas antes)"
        keyboardType="number-pad"
        value={form.notice}
        onChangeText={(v) => handleChange('notice', v)}
      />
      <TextField
        label="Reglas extra (opcional)"
        value={form.extraRules}
        onChangeText={(v) => handleChange('extraRules', v)}
      />
      <TextField
        label="Mensaje para el rival (opcional)"
        value={form.note}
        onChangeText={(v) => handleChange('note', v)}
      />
      {controller.error ? <Text style={styles.error}>{controller.error}</Text> : null}
      {action.message ? (
        <Text style={styles.message} accessibilityLiveRegion="polite">
          {action.message}
        </Text>
      ) : null}
      <PrimaryButton
        label="Enviar y firmar propuesta"
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
