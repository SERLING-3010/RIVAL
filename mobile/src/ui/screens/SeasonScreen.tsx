// Temporada de la liga: tabla de posiciones y calendario. El personal arma el calendario y asigna árbitros.

import { useState } from 'react';
import { StyleSheet, Text } from 'react-native';

import type { SeasonController } from '../../controllers/useSeason';
import { formatLocal } from '../../domain/dateTime';
import type { RefereeEntry } from '../../domain/leagueModels';
import { groupByRound } from '../../domain/seasonModels';
import { Card } from '../components/Card';
import { ChoiceChips } from '../components/ChoiceChips';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { TextField } from '../components/TextField';
import { colors, font } from '../theme';

interface Props {
  controller: SeasonController;
  canManage: boolean;
  referees: RefereeEntry[];
  onBack: () => void;
}

export function SeasonScreen({ controller, canManage, referees, onBack }: Props) {
  const [first, setFirst] = useState('');
  const [days, setDays] = useState('7');
  const [error, setError] = useState<string | null>(null);
  const [picked, setPicked] = useState<Record<number, number>>({});
  const busy = controller.action.busy;
  return (
    <Screen title="Calendario y tabla" onBack={onBack}>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {({ calendar, table }) => (
          <>
            <Card
              title="Tabla de posiciones"
              subtitle="PJ · G-E-P · GF:GC · Pts (solo resultados confirmados)"
            >
              {table.map((r, i) => (
                <Text key={r.team_id} style={styles.line}>
                  {i + 1}. {r.name} · {r.played} · {r.won}-{r.drawn}-{r.lost} · {r.goals_for}:
                  {r.goals_against} · {r.points} pts
                </Text>
              ))}
            </Card>
            {calendar.length === 0 && canManage ? (
              <Card title="Armar calendario (todos contra todos)">
                <TextField label="Primera fecha (dd/mm/aaaa hh:mm)" value={first} onChangeText={setFirst} />
                <TextField
                  label="Días entre fechas"
                  keyboardType="number-pad"
                  value={days}
                  onChangeText={setDays}
                />
                {error ? <Text style={styles.error}>{error}</Text> : null}
                <PrimaryButton
                  label="Generar calendario"
                  disabled={busy}
                  onPress={() => void controller.handleGenerate(first, days).then(setError)}
                />
              </Card>
            ) : null}
            {calendar.length === 0 && !canManage ? (
              <Text style={styles.meta}>El organizador aún no arma el calendario.</Text>
            ) : null}
            {groupByRound(calendar).map(({ round, matches }) => (
              <Card key={round} title={`Fecha ${round}`}>
                {matches.map((m) => (
                  <Card
                    key={m.contract_id}
                    title={`${m.host.name} ${m.result ?? 'vs'} ${m.guest.name}`}
                    subtitle={formatLocal(m.kickoff_at)}
                  >
                    {canManage && !m.result && referees.length > 0 ? (
                      <>
                        <ChoiceChips
                          label="Árbitro"
                          selected={picked[m.contract_id] ? [String(picked[m.contract_id])] : []}
                          choices={referees.map((r) => ({ value: String(r.user_id), label: r.display_name }))}
                          onToggle={(v) => setPicked((p) => ({ ...p, [m.contract_id]: Number(v) }))}
                        />
                        <PrimaryButton
                          label="Asignar árbitro"
                          variant="secondary"
                          disabled={busy || !picked[m.contract_id]}
                          onPress={() =>
                            void controller.handleAssign(m.contract_id, picked[m.contract_id] ?? 0)
                          }
                        />
                      </>
                    ) : null}
                  </Card>
                ))}
              </Card>
            ))}
          </>
        )}
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
  meta: { color: colors.textMuted, fontSize: font.small },
  error: { color: colors.danger, fontSize: font.body },
});
