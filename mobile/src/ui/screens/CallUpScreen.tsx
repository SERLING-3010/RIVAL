// Convocatoria del partido: el administrador convoca; cada jugador convocado responde si va.

import { useState } from 'react';
import { StyleSheet, Text } from 'react-native';

import type { CallUpController } from '../../controllers/useMatchday';
import type { SquadMember } from '../../domain/managerModels';
import { CALLUP_STATUS_LABEL } from '../../domain/matchdayModels';
import { Card } from '../components/Card';
import { ChoiceChips } from '../components/ChoiceChips';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { colors, font } from '../theme';

interface Props {
  controller: CallUpController;
  squad: SquadMember[];
  isAdmin: boolean;
  myUserId: number;
  onBack: () => void;
}

export function CallUpScreen({ controller, squad, isAdmin, myUserId, onBack }: Props) {
  const [picked, setPicked] = useState<number[]>([]);
  const busy = controller.action.busy;
  const toggle = (id: number) => setPicked((p) => (p.includes(id) ? p.filter((x) => x !== id) : [...p, id]));
  return (
    <Screen title="Convocatoria" onBack={onBack}>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(callup) => {
          const called = new Set(callup.items.map((i) => i.user_id));
          const me = callup.items.find((i) => i.user_id === myUserId);
          const free = squad.filter((m) => !called.has(m.user_id));
          return (
            <>
              <Card
                title={`Van ${callup.going} · No van ${callup.not_going} · Sin responder ${callup.pending}`}
              >
                {callup.items.map((i) => (
                  <Text key={i.user_id} style={styles.line}>
                    {i.display_name}: {CALLUP_STATUS_LABEL[i.status]}
                  </Text>
                ))}
              </Card>
              {me ? (
                <Card title={`Tu respuesta: ${CALLUP_STATUS_LABEL[me.status]}`}>
                  <PrimaryButton
                    label="Voy"
                    disabled={busy}
                    onPress={() => void controller.handleRespond(true)}
                  />
                  <PrimaryButton
                    label="No voy"
                    variant="secondary"
                    disabled={busy}
                    onPress={() => void controller.handleRespond(false)}
                  />
                </Card>
              ) : null}
              {isAdmin && free.length > 0 ? (
                <Card title="Convocar jugadores">
                  <ChoiceChips
                    label="Plantilla sin convocar"
                    selected={picked.map(String)}
                    choices={free.map((m) => ({ value: String(m.user_id), label: m.display_name }))}
                    onToggle={(v) => toggle(Number(v))}
                  />
                  <PrimaryButton
                    label="Enviar convocatoria"
                    disabled={busy || picked.length === 0}
                    onPress={() => void controller.handleSend(picked).then(() => setPicked([]))}
                  />
                </Card>
              ) : null}
            </>
          );
        }}
      </StateView>
      {controller.action.message ? (
        <Text style={styles.line} accessibilityLiveRegion="polite">
          {controller.action.message}
        </Text>
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  line: { color: colors.text, fontSize: font.small },
});
