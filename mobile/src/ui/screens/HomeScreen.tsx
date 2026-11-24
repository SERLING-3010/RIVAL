// Inicio según el rol. Lo que llega en Sprints futuros se rotula "Próximamente".

import { StyleSheet, Text } from 'react-native';

import { roleTitle, TEAM_ROLE_LABEL } from '../../domain/labels';
import type { ModerationMe } from '../../domain/moderationModels';
import { pendingCardTitle } from '../../domain/pendingModels';
import type { MyTeam, User } from '../../domain/models';
import type { ViewState } from '../../domain/viewState';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { TrustCards } from '../components/TrustCards';
import { colors, font } from '../theme';

interface Props {
  user: User;
  myTeams: ViewState<MyTeam[]>;
  onRefreshTeams: () => void;
  onSearchTeam: () => void;
  onCreateTeam: () => void;
  onFreeAgent: () => void;
  onLeagues: () => void;
  onMyVenues: () => void;
  onTransferOffers: () => void;
  onRefereeMatches: () => void;
  onMyCallUps: () => void;
  pendingCount: number | null;
  onPending: () => void;
  moderation: ModerationMe | null;
  onMySanctions: () => void;
  onModeration: () => void;
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
  onLeagues,
  onMyVenues,
  onTransferOffers,
  onRefereeMatches,
  onMyCallUps,
  pendingCount,
  onPending,
  moderation,
  onMySanctions,
  onModeration,
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
      <TrustCards me={moderation} onMySanctions={onMySanctions} onModeration={onModeration} />
      <Card
        title={pendingCardTitle(pendingCount)}
        subtitle="Firmas, marcadores, convocatorias, traspasos y más: lo que espera tu acción"
        onPress={onPending}
      />
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
            title="Mis convocatorias"
            subtitle="Partidos a los que te convocaron: responde si vas"
            onPress={onMyCallUps}
          />
          <Card
            title="Ofertas de traspaso"
            subtitle="Equipos que quieren ficharte: tú decides si te vas"
            onPress={onTransferOffers}
          />
          <Card
            title="Agente libre e invitaciones"
            subtitle="Deja que los DT te encuentren y responde invitaciones"
            onPress={onFreeAgent}
          />
        </>
      ) : null}
      {hasTeam || user.roles.includes('REFEREE') ? (
        <Card
          title="Ligas"
          subtitle={
            user.roles.includes('REFEREE')
              ? 'Busca o crea ligas y únete a su cuerpo arbitral'
              : 'Busca o crea ligas e inscribe a tu equipo'
          }
          onPress={onLeagues}
        />
      ) : null}
      {user.roles.includes('REFEREE') ? (
        <Card
          title="Mis partidos como árbitro"
          subtitle="Acepta partidos de tus ligas y fija el resultado"
          onPress={onRefereeMatches}
        />
      ) : null}
      {user.roles.includes('VENUE_OWNER') ? (
        <Card
          title="Mi establecimiento"
          subtitle="Registra canchas, publica franjas y confirma reservas"
          onPress={onMyVenues}
        />
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
