// Acciones del equipo en "Mi equipo": buscar rival, partidos pactados (contratos), partidos para
// responder, búsquedas de partido y agentes libres. Todos navegan; el backend decide quién actúa.

import type { Navigator } from '../controllers/useNavigator';
import type { TeamSummary } from '../domain/models';
import { PrimaryButton } from '../ui/components/PrimaryButton';

interface Props {
  team: TeamSummary;
  isAdmin: boolean;
  navigator: Navigator;
}

export function TeamActions({ team, isAdmin, navigator }: Props) {
  return (
    <>
      <PrimaryButton
        label="Buscar rival"
        onPress={() => navigator.push({ name: 'rivals', teamId: team.id, isAdmin })}
      />
      <PrimaryButton
        label="Modo manager"
        onPress={() => navigator.push({ name: 'manager', teamId: team.id })}
      />
      <PrimaryButton
        label="Partidos pactados"
        variant="secondary"
        onPress={() => navigator.push({ name: 'contracts', teamId: team.id })}
      />
      <PrimaryButton
        label="Actividad del equipo"
        variant="secondary"
        onPress={() =>
          navigator.push({ name: 'activity', scope: 'teams', id: team.id, title: 'Actividad del equipo' })
        }
      />
      <PrimaryButton
        label="Partidos para mi equipo"
        variant="secondary"
        onPress={() => navigator.push({ name: 'matchFeed', teamId: team.id, isAdmin })}
      />
      <PrimaryButton
        label="Nuestras búsquedas de partido"
        variant="secondary"
        onPress={() => navigator.push({ name: 'matchRequests', teamId: team.id, isAdmin })}
      />
      {isAdmin ? (
        <PrimaryButton
          label="Equipos bloqueados"
          variant="secondary"
          onPress={() => navigator.push({ name: 'blockedTeams', teamId: team.id })}
        />
      ) : null}
      {isAdmin ? (
        <PrimaryButton
          label="Buscar agentes libres"
          variant="secondary"
          onPress={() => navigator.push({ name: 'freeAgentSearch', team })}
        />
      ) : null}
    </>
  );
}
