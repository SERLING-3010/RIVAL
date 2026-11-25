// Rivales sugeridos: cada tarjeta dice por qué aparece. Son reglas a la vista, no un algoritmo oculto.

import { StyleSheet, Text } from 'react-native';

import type { Loader } from '../../controllers/useLoader';
import type { Suggestion } from '../../domain/suggestionModels';
import { suggestionSubtitle } from '../../domain/suggestionModels';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { colors, font } from '../theme';

interface Props {
  controller: Loader<Suggestion[]>;
  canChallenge: boolean;
  onChallenge: (teamId: number) => void;
  onBack: () => void;
}

export function SuggestionsScreen({ controller, canChallenge, onChallenge, onBack }: Props) {
  return (
    <Screen title="Rivales sugeridos" onBack={onBack}>
      <Text style={styles.meta}>
        Te sugerimos equipos por cercanía (en rangos), nivel parecido y días en que juegan. No mostramos
        ubicaciones exactas.
      </Text>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(items) =>
          items.map((s) => (
            <Card key={s.team.id} title={s.team.name} subtitle={suggestionSubtitle(s)}>
              {s.reasons.map((r) => (
                <Text key={r} style={styles.reason}>
                  • {r}
                </Text>
              ))}
              {canChallenge ? <PrimaryButton label="Retar" onPress={() => onChallenge(s.team.id)} /> : null}
            </Card>
          ))
        }
      </StateView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  reason: { color: colors.text, fontSize: font.body },
  meta: { color: colors.textMuted, fontSize: font.small },
});
