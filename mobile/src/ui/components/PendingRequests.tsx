// Solicitudes pendientes de una liga: solo las ve el personal, y cada quien decide lo que le toca.

import { StyleSheet, Text } from 'react-native';

import type { EntryKind, LeagueDetail } from '../../domain/leagueModels';
import { colors, font } from '../theme';
import { Card } from './Card';
import { PrimaryButton } from './PrimaryButton';

interface Props {
  detail: LeagueDetail;
  canDecideTeams: boolean;
  canDecideReferees: boolean;
  busy: boolean;
  onDecide: (kind: EntryKind, entryId: number, decision: 'approve' | 'reject') => Promise<void>;
}

interface Row {
  kind: EntryKind;
  id: number;
  title: string;
}

export function PendingRequests({ detail, canDecideTeams, canDecideReferees, busy, onDecide }: Props) {
  const rows: Row[] = [
    ...(canDecideTeams
      ? detail.pending_teams.map((e) => ({
          kind: 'team' as const,
          id: e.id,
          title: `Equipo: ${e.team.name}`,
        }))
      : []),
    ...(canDecideReferees
      ? detail.pending_referees.map((r) => ({
          kind: 'referee' as const,
          id: r.id,
          title: `Árbitro: ${r.display_name}`,
        }))
      : []),
  ];
  if (rows.length === 0) return null;
  return (
    <Card title={`Solicitudes por revisar (${rows.length})`}>
      <Text style={styles.meta}>Aprobar inscribe al equipo o al árbitro en la liga.</Text>
      {rows.map((row) => (
        <Card key={`${row.kind}-${row.id}`} title={row.title}>
          <PrimaryButton
            label="Aprobar"
            disabled={busy}
            onPress={() => void onDecide(row.kind, row.id, 'approve')}
          />
          <PrimaryButton
            label="Rechazar"
            variant="secondary"
            disabled={busy}
            onPress={() => void onDecide(row.kind, row.id, 'reject')}
          />
        </Card>
      ))}
    </Card>
  );
}

const styles = StyleSheet.create({
  meta: { color: colors.textMuted, fontSize: font.small },
});
