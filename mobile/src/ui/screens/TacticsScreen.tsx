// Alineación táctica: formación, titulares con posición y suplentes. Solo la ve tu equipo.

import { useState } from 'react';
import { StyleSheet, Text } from 'react-native';

import type { TacticsController } from '../../controllers/useTactics';
import type { Role, Tactic } from '../../domain/tacticsModels';
import { allPlayers, draftFrom } from '../../domain/tacticsModels';
import { Card } from '../components/Card';
import { ChoiceChips } from '../components/ChoiceChips';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { TacticPlayerRow } from '../components/TacticPlayerRow';
import { colors, font } from '../theme';

interface Props {
  controller: TacticsController;
  onBack: () => void;
}

function TacticEditor({ tactic, controller }: { tactic: Tactic; controller: TacticsController }) {
  const [draft, setDraft] = useState(() => draftFrom(tactic));
  const [error, setError] = useState<string | null>(null);
  const players = allPlayers(tactic);
  const setRole = (id: number, role: Role) => setDraft((d) => ({ ...d, roles: { ...d.roles, [id]: role } }));
  const setPosition = (id: number, text: string) =>
    setDraft((d) => ({ ...d, positions: { ...d.positions, [id]: text } }));
  return (
    <>
      {tactic.uses_formation && tactic.can_edit ? (
        <ChoiceChips
          label="Formación (sin el arquero)"
          choices={tactic.suggested_formations.map((f) => ({ value: f, label: f }))}
          selected={draft.formation ? [draft.formation] : []}
          onToggle={(f) => setDraft((d) => ({ ...d, formation: d.formation === f ? null : f }))}
        />
      ) : null}
      {tactic.formation && !tactic.can_edit ? <Text style={styles.title}>{tactic.formation}</Text> : null}
      <Card title={`Titulares: ${tactic.players_per_side}`}>
        {players.length === 0 ? (
          <Text style={styles.meta}>
            Aún no hay convocados que confirmaron. Envía la convocatoria primero.
          </Text>
        ) : null}
        {players.map((p) => (
          <TacticPlayerRow
            key={p.user_id}
            player={p}
            role={draft.roles[p.user_id] ?? 'out'}
            position={draft.positions[p.user_id] ?? ''}
            editable={tactic.can_edit}
            onRole={(role) => setRole(p.user_id, role)}
            onPosition={(text) => setPosition(p.user_id, text)}
          />
        ))}
      </Card>
      {tactic.can_edit ? (
        <PrimaryButton
          label="Guardar alineación"
          disabled={controller.action.busy}
          onPress={() => void controller.handleSave(draft, tactic).then(setError)}
        />
      ) : null}
      {error ? <Text style={styles.error}>{error}</Text> : null}
    </>
  );
}

export function TacticsScreen({ controller, onBack }: Props) {
  return (
    <Screen title="Alineación táctica" onBack={onBack}>
      <Text style={styles.meta}>
        Solo la ve tu equipo; el rival no. Entran los convocados que dijeron que van.
      </Text>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(tactic) => (
          <TacticEditor
            key={`${tactic.formation}|${tactic.starters.length}|${tactic.subs.length}`}
            tactic={tactic}
            controller={controller}
          />
        )}
      </StateView>
      {controller.action.message ? (
        <Text style={styles.meta} accessibilityLiveRegion="polite">
          {controller.action.message}
        </Text>
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  title: { color: colors.text, fontSize: font.heading, fontWeight: '700' },
  meta: { color: colors.textMuted, fontSize: font.small },
  error: { color: colors.danger, fontSize: font.body },
});
