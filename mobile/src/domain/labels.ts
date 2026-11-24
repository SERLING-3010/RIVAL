import type { TeamRole, UserRole } from './models';

export interface RoleOption {
  role: UserRole;
  title: string;
  description: string;
}

export const ROLE_OPTIONS: RoleOption[] = [
  { role: 'PLAYER', title: 'Jugador', description: 'Busca equipo o crea el tuyo y juega partidos.' },
  { role: 'COACH', title: 'Director técnico', description: 'Arma tu plantilla y administra tu equipo.' },
  { role: 'REFEREE', title: 'Árbitro', description: 'Únete a ligas y arbitra partidos cerca de ti.' },
  {
    role: 'VENUE_OWNER',
    title: 'Establecimiento deportivo',
    description: 'Publica tus canchas y horarios.',
  },
];

export const TEAM_ROLE_LABEL: Record<TeamRole, string> = {
  COACH: 'DT',
  CAPTAIN: 'Capitán',
  PLAYER: 'Jugador',
};

export function roleTitle(role: UserRole): string {
  return ROLE_OPTIONS.find((option) => option.role === role)?.title ?? role;
}
