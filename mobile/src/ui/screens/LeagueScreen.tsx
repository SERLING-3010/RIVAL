import { StyleSheet, Text } from 'react-native';

import type { LeagueController } from '../../controllers/useLeagues';
import type { TransferWindowController } from '../../controllers/useTransferWindow';
import { ENTRY_STATUS_LABEL, leagueActions, myEntries, STAFF_ROLE_LABEL } from '../../domain/leagueRules';
import type { MyTeam, User } from '../../domain/models';
import { Card } from '../components/Card';
import { useFeatures } from '../FeaturesContext';
import { PendingRequests } from '../components/PendingRequests';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { SeasonCloseCard } from '../components/SeasonCloseCard';
import { StateView } from '../components/StateView';
import { TransferWindowCard } from '../components/TransferWindowCard';
import { colors, font } from '../theme';

interface Props {
  controller: LeagueController;
  user: User;
  myTeams: MyTeam[];
  onSeason: (canManage: boolean) => void;
  onCup: (canManage: boolean) => void;
  windowController: TransferWindowController;
  onBack: () => void;
}

export function LeagueScreen({
  controller,
  user,
  myTeams,
  onSeason,
  onCup,
  windowController,
  onBack,
}: Props) {
  const busy = controller.action.busy;
  const features = useFeatures();
  return (
    <Screen title="Liga" onBack={onBack}>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(detail) => {
          const can = leagueActions(detail, user, myTeams);
          const l = detail.league;
          const mine = myEntries(detail);
          return (
            <>
              <Text style={styles.title}>{l.name}</Text>
              <Text style={styles.meta}>
                {l.modality_code} · {l.city} · Temporada {l.season}
                {detail.my_role ? ` · Eres ${STAFF_ROLE_LABEL[detail.my_role].toLowerCase()}` : ''}
              </Text>
              {detail.description ? <Text style={styles.line}>{detail.description}</Text> : null}
              <Card title={`Equipos (${detail.teams.length})`}>
                {detail.teams.map((e) => (
                  <Text key={e.id} style={styles.line}>
                    {e.team.name} · {e.team.neighborhood}
                  </Text>
                ))}
              </Card>
              {features.referees ? ( // Sprint 29: sin árbitros en el lanzamiento
                <Card title={`Cuerpo arbitral (${detail.referees.length})`}>
                  {detail.referees.map((r) => (
                    <Text key={r.id} style={styles.line}>
                      {r.display_name}
                    </Text>
                  ))}
                </Card>
              ) : null}
              <SeasonCloseCard
                detail={detail}
                busy={busy}
                onClose={() => void controller.handleCloseSeason()}
              />
              <PrimaryButton label="Calendario y tabla" onPress={() => onSeason(can.canDecideTeams)} />
              <PrimaryButton
                label="Copa eliminatoria"
                variant="secondary"
                onPress={() => onCup(can.canDecideTeams)}
              />
              <TransferWindowCard
                start={detail.transfer_window_start}
                end={detail.transfer_window_end}
                canEdit={detail.my_role === 'ORGANIZER' || detail.my_role === 'CO_ORGANIZER'}
                controller={windowController}
              />
              <Card title="Personal">
                {detail.staff.map((m) => (
                  <Text key={m.user_id} style={styles.line}>
                    {m.display_name} · {STAFF_ROLE_LABEL[m.role]}
                  </Text>
                ))}
              </Card>
              {mine.map((m) => (
                <Card key={`${m.kind}-${m.id}`} title={m.name} badge={ENTRY_STATUS_LABEL[m.status]}>
                  <PrimaryButton
                    label={m.status === 'APPROVED' ? 'Salir de la liga' : 'Retirar solicitud'}
                    variant="secondary"
                    disabled={busy}
                    onPress={() => void controller.handleDecide(m.kind, m.id, 'withdraw')}
                  />
                </Card>
              ))}
              {can.eligibleTeams.map((t) => (
                <PrimaryButton
                  key={t.team.id}
                  label={`Inscribir a ${t.team.name}`}
                  disabled={busy}
                  onPress={() => void controller.handleRequestTeam(t.team.id)}
                />
              ))}
              {can.canJoinAsReferee && features.referees ? (
                <PrimaryButton
                  label="Unirme al cuerpo arbitral"
                  disabled={busy}
                  onPress={() => void controller.handleJoinAsReferee()}
                />
              ) : null}
              <PendingRequests
                detail={detail}
                canDecideTeams={can.canDecideTeams}
                canDecideReferees={can.canDecideReferees}
                busy={busy}
                onDecide={controller.handleDecide}
              />
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
  title: { color: colors.text, fontSize: font.heading, fontWeight: '700' },
  line: { color: colors.text, fontSize: font.small },
  meta: { color: colors.textMuted, fontSize: font.small },
});
