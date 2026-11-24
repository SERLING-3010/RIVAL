// Inicio según el rol. Lo que llega en Sprints futuros se rotula "Próximamente".

import { StyleSheet, Text } from 'react-native';

import { roleTitle, TEAM_ROLE_LABEL } from '../../domain/labels';
import type { MyTeam, User } from '../../domain/models';
import type { ViewState } from '../../domain/viewState';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { colors, font } from '../theme';

interface Props {
  user: User;
  myTeams: ViewState<MyTeam[]>;
  onRefreshTeams: () => void;
  onSearchTeam: () => void;
  onCreateTeam: () => void;
  onFreeAgent: () => void;
  onOpenTeam: (teamId: number) => void;
  onLogout: () => void;
}

export function HomeScreen({
  user,
  myTeams,
  onRefreshTeams,
  onSearchTeam,
  onCreateTeam,
  onFreeAgent,
  onOpenTeam,
  onLogout,
}: Props) {
  const plays = user.roles.includes('PLAYER') || user.roles.includes('COACH');
  const hasTeam = myTeams.kind === 'success';
  return (
    <Screen title={`Hola, ${user.display_name}`}>
      <Text style={styles.lead}>
        {user.roles.map(roleTitle).join(' · ')} · {user.neighborhood}, {user.city}
      </Text>
      {plays ? (
        <>
          <Text style={styles.section} accessibilityRole="header">
            Mis equipos
          </Text>
          <StateView
            state={myTeams}
            onRetry={onRefreshTeams}
            emptyAction={{ label: 'Buscar equipo', onPress: onSearchTeam }}
          >
            {(teams) =>
              teams.map((item) => (
                <Card
                  key={item.team.id}
                  title={item.team.name}
                  subtitle={`${item.team.modality_code} · ${item.team.neighborhood}, ${item.team.city}`}
                  badge={item.is_admin ? 'Administras' : TEAM_ROLE_LABEL[item.my_role]}
                  onPress={() => onOpenTeam(item.team.id)}
                >
                  {item.is_admin && item.pending_requests > 0 ? (
                    <Text style={styles.pending}>{item.pending_requests} solicitud(es) por revisar</Text>
                  ) : null}
                </Card>
              ))
            }
          </StateView>
          <PrimaryButton label="Buscar equipo" variant="secondary" onPress={onSearchTeam} />
          <PrimaryButton label="Crear equipo" onPress={onCreateTeam} />
          <Card
            title="Agente libre e invitaciones"
            subtitle="Deja que los DT te encuentren y responde invitaciones"
            onPress={onFreeAgent}
          />
          {hasTeam ? <Card title="Ligas" subtitle="Buscar o crear liga · Próximamente (Sprint 3)" /> : null}
        </>
      ) : null}
      {user.roles.includes('REFEREE') ? (
        <Card title="Buscar liga" subtitle="Únete al cuerpo arbitral de una liga · Próximamente (Sprint 3)" />
      ) : null}
      {user.roles.includes('VENUE_OWNER') ? (
        <Card title="Mi establecimiento" subtitle="Registra canchas y horarios · Próximamente (Sprint 3)" />
      ) : null}
      <PrimaryButton label="Cerrar sesión" variant="secondary" onPress={onLogout} />
    </Screen>
  );
}

const styles = StyleSheet.create({
  lead: { color: colors.textMuted, fontSize: font.body },
  section: { color: colors.text, fontSize: font.heading, fontWeight: '700' },
  pending: { color: colors.warning, fontSize: font.small, fontWeight: '600' },
});
