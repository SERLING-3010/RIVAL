import { StyleSheet, Text } from 'react-native';

import type { TeamSearchController } from '../../controllers/useTeamSearch';
import type { Sport, TeamSummary } from '../../domain/models';
import { Card } from '../components/Card';
import { ChoiceChips } from '../components/ChoiceChips';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { TextField } from '../components/TextField';
import { colors, font } from '../theme';

interface Props {
  controller: TeamSearchController;
  sports: Sport[];
  canJoinAsCoach: boolean;
  onCreateTeam: () => void;
  onBack: () => void;
}

export function TeamSearchScreen({ controller, sports, canJoinAsCoach, onCreateTeam, onBack }: Props) {
  const sportName = (code: string) => sports.find((s) => s.code === code)?.name ?? code;
  const renderJoin = (team: TeamSummary) => {
    const status = controller.joinStatus[team.id];
    if (status?.kind === 'sent') {
      return (
        <Text style={styles.sent} accessibilityLiveRegion="polite">
          {status.message}
        </Text>
      );
    }
    return (
      <>
        {status?.kind === 'failed' ? <Text style={styles.failed}>{status.message}</Text> : null}
        <PrimaryButton
          label="Solicitar unirme"
          loading={status?.kind === 'sending'}
          onPress={() => void controller.handleRequestJoin(team.id, 'PLAYER')}
        />
        {canJoinAsCoach && !team.has_coach ? (
          <PrimaryButton
            label="Unirme como DT"
            variant="secondary"
            disabled={status?.kind === 'sending'}
            onPress={() => void controller.handleRequestJoin(team.id, 'COACH')}
          />
        ) : null}
      </>
    );
  };
  return (
    <Screen title="Buscar equipo" onBack={onBack}>
      <ChoiceChips
        label="Deporte"
        selected={controller.sport ? [controller.sport] : []}
        choices={sports.map((s) => ({ value: s.code, label: s.name }))}
        onToggle={(code) => controller.handleSport(controller.sport === code ? null : code)}
      />
      <TextField label="Ciudad" value={controller.city} onChangeText={controller.handleCity} />
      <TextField
        label="Nombre del equipo (opcional)"
        value={controller.text}
        onChangeText={controller.handleText}
      />
      <PrimaryButton label="Buscar" variant="secondary" onPress={controller.handleSearch} />
      <StateView
        state={controller.state}
        onRetry={controller.handleSearch}
        emptyAction={{ label: 'Crear mi equipo', onPress: onCreateTeam }}
      >
        {(page) => (
          <>
            <Text style={styles.count}>{page.total} equipo(s) encontrados</Text>
            {page.items.map((team) => (
              <Card
                key={team.id}
                title={team.name}
                subtitle={`${sportName(team.sport_code)} ${team.modality_code} · ${team.neighborhood}, ${team.city} · ${team.member_count} jugador(es)`}
                badge={team.has_coach ? 'Con DT' : 'Sin DT'}
              >
                {renderJoin(team)}
              </Card>
            ))}
            {controller.hasMore ? (
              <PrimaryButton
                label="Cargar más"
                variant="secondary"
                loading={controller.loadingMore}
                onPress={() => void controller.handleLoadMore()}
              />
            ) : null}
          </>
        )}
      </StateView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  count: { color: colors.textMuted, fontSize: font.small },
  sent: { color: colors.success, fontSize: font.small, fontWeight: '600' },
  failed: { color: colors.danger, fontSize: font.small },
});
