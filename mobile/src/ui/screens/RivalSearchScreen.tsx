import { StyleSheet, Text } from 'react-native';

import type { RivalSearchController } from '../../controllers/useScouting';
import type { TeamSummary } from '../../domain/models';
import { levelText } from '../../domain/matchdayModels';
import { SCOPE_LABEL, distanceText } from '../../domain/matchLabels';
import type { SearchScope } from '../../domain/matchModels';
import { Card } from '../components/Card';
import { ChoiceChips } from '../components/ChoiceChips';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { LoadMore } from '../components/LoadMore';
import { StateView } from '../components/StateView';
import { colors, font } from '../theme';

interface Props {
  controller: RivalSearchController;
  canChallenge: boolean;
  onChallenge: (teamId: number) => void;
  onReport: (team: TeamSummary) => void;
  onBlock: (teamId: number) => void;
  onBack: () => void;
}

const SCOPES: SearchScope[] = ['NEARBY', 'NEIGHBORHOOD', 'CITY'];
const RADII = [2, 5, 10, 15];

export function RivalSearchScreen({
  controller,
  canChallenge,
  onChallenge,
  onBack,
  onReport,
  onBlock,
}: Props) {
  return (
    <Screen title="Buscar rival" onBack={onBack}>
      <Text style={styles.note}>
        Solo se muestran barrios y distancias aproximadas, nunca ubicaciones exactas.
      </Text>
      <ChoiceChips
        label="Alcance"
        selected={[controller.scope]}
        choices={SCOPES.map((s) => ({ value: s, label: SCOPE_LABEL[s] }))}
        onToggle={(value) => controller.handleScope(value as SearchScope)}
      />
      {controller.scope === 'NEARBY' ? (
        <ChoiceChips
          label="Radio"
          selected={[String(controller.radiusKm)]}
          choices={RADII.map((km) => ({ value: String(km), label: `${km} km` }))}
          onToggle={(value) => controller.handleRadius(Number(value))}
        />
      ) : null}
      <ChoiceChips
        label="Ordenar"
        selected={[controller.order]}
        choices={[
          { value: 'default', label: controller.scope === 'NEARBY' ? 'Más cerca' : 'Por nombre' },
          { value: 'level', label: 'Nivel parecido' },
        ]}
        onToggle={(value) => controller.handleOrder(value === 'level' ? 'level' : 'default')}
      />
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(page) => (
          <>
            {page.items.map((rival) => (
              <Card
                key={rival.team.id}
                title={rival.team.name}
                subtitle={`${rival.team.neighborhood}, ${rival.team.city} ${distanceText(rival.distance_band)} · ${rival.team.member_count} jugador(es) · ${levelText(rival.level, rival.level_reliable)}`}
                badge={rival.team.has_coach ? 'Con DT' : 'Sin DT'}
              >
                {canChallenge ? (
                  <PrimaryButton
                    label="Retar"
                    variant="secondary"
                    onPress={() => onChallenge(rival.team.id)}
                  />
                ) : null}
                <PrimaryButton label="Reportar" variant="secondary" onPress={() => onReport(rival.team)} />
                {canChallenge ? (
                  <PrimaryButton label="Bloquear" variant="danger" onPress={() => onBlock(rival.team.id)} />
                ) : null}
              </Card>
            ))}
            <LoadMore
              hasMore={controller.hasMore}
              loading={controller.loadingMore}
              error={controller.moreError}
              onPress={() => void controller.handleLoadMore()}
            />
          </>
        )}
      </StateView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  note: { color: colors.textMuted, fontSize: font.small },
});
