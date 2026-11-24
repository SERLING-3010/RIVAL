// Mi equipo: plantilla, administrador y solicitudes. Salir pide confirmación.

import type { ReactNode } from 'react';
import { Alert, StyleSheet, Text } from 'react-native';

import type { TeamDetailController } from '../../controllers/useTeamDetail';
import { TEAM_ROLE_LABEL } from '../../domain/labels';
import type { TeamSummary } from '../../domain/models';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { colors, font } from '../theme';

interface Props {
  controller: TeamDetailController;
  renderActions?: (team: TeamSummary, isAdmin: boolean) => ReactNode;
  userId: number;
  onBack: () => void;
}

export function TeamScreen({ controller, userId, renderActions, onBack }: Props) {
  const myRole =
    controller.detail.kind === 'success'
      ? controller.detail.data.members.find((m) => m.user_id === userId)?.role
      : undefined;
  const confirmCaptain = (memberId: number, name: string) => {
    if (myRole !== 'CAPTAIN') {
      void controller.handleSetCaptain(memberId);
      return;
    }
    Alert.alert(
      '¿Pasar la capitanía?',
      `${name} será el capitán y administrará el equipo. Tú pasas a jugador.`,
      [
        { text: 'Cancelar', style: 'cancel' },
        { text: 'Confirmar', onPress: () => void controller.handleSetCaptain(memberId) },
      ],
    );
  };
  const confirmLeave = () =>
    Alert.alert('¿Salir del equipo?', 'Dejarás de ver sus partidos y convocatorias.', [
      { text: 'Cancelar', style: 'cancel' },
      { text: 'Salir', style: 'destructive', onPress: () => void controller.handleLeave() },
    ]);
  return (
    <Screen title="Mi equipo" onBack={onBack}>
      <StateView state={controller.detail} onRetry={controller.handleRefresh}>
        {(detail) => (
          <>
            <Text style={styles.teamName} accessibilityRole="header">
              {detail.team.name}
            </Text>
            <Text style={styles.meta}>
              {detail.team.modality_code} · {detail.team.neighborhood}, {detail.team.city}
            </Text>
            {renderActions?.(detail.team, controller.isAdmin)}
            <Text style={styles.section} accessibilityRole="header">
              Plantilla ({detail.members.length})
            </Text>
            {detail.members.map((member) => (
              <Card
                key={member.user_id}
                title={member.user_id === userId ? `${member.display_name} (tú)` : member.display_name}
                subtitle={member.position ?? undefined}
                badge={
                  member.user_id === detail.admin_user_id
                    ? `${TEAM_ROLE_LABEL[member.role]} · Admin`
                    : TEAM_ROLE_LABEL[member.role]
                }
              >
                {controller.isAdmin && member.role === 'PLAYER' ? (
                  <PrimaryButton
                    label="Nombrar capitán"
                    variant="secondary"
                    disabled={controller.busy}
                    onPress={() => confirmCaptain(member.user_id, member.display_name)}
                  />
                ) : null}
              </Card>
            ))}
          </>
        )}
      </StateView>
      {controller.isAdmin ? (
        <>
          <Text style={styles.section} accessibilityRole="header">
            Solicitudes para unirse
          </Text>
          <StateView state={controller.requests} onRetry={controller.handleRefresh}>
            {(requests) =>
              requests.map((request) => (
                <Card
                  key={request.id}
                  title={request.display_name}
                  subtitle={
                    request.desired_role === 'COACH'
                      ? 'Quiere entrar como DT. Si lo aceptas, el DT pasa a administrar el equipo.'
                      : `Quiere entrar como ${TEAM_ROLE_LABEL[request.desired_role]}`
                  }
                >
                  <PrimaryButton
                    label="Aceptar"
                    disabled={controller.busy}
                    onPress={() => void controller.handleDecide(request.id, true)}
                  />
                  <PrimaryButton
                    label="Rechazar"
                    variant="secondary"
                    disabled={controller.busy}
                    onPress={() => void controller.handleDecide(request.id, false)}
                  />
                </Card>
              ))
            }
          </StateView>
        </>
      ) : null}
      {controller.actionMessage ? (
        <Text style={styles.message} accessibilityLiveRegion="polite">
          {controller.actionMessage}
        </Text>
      ) : null}
      <PrimaryButton
        label="Salir del equipo"
        variant="danger"
        loading={controller.busy}
        onPress={confirmLeave}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  teamName: { color: colors.text, fontSize: font.title, fontWeight: '700' },
  meta: { color: colors.textMuted, fontSize: font.body },
  section: { color: colors.text, fontSize: font.heading, fontWeight: '700' },
  message: { color: colors.text, fontSize: font.body },
});
