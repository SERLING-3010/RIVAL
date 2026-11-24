import type { FeedController } from '../../controllers/useMatches';
import { formatLocal } from '../../domain/dateTime';
import { PLACE_LABEL, REFEREE_LABEL, SCOPE_LABEL, distanceText } from '../../domain/matchLabels';
import type { MatchRequest, SearchScope } from '../../domain/matchModels';
import { Card } from '../components/Card';
import { ChoiceChips } from '../components/ChoiceChips';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';

interface Props {
  controller: FeedController;
  isAdmin: boolean;
  onOffer: (request: MatchRequest) => void;
  onMyOffers: (request: MatchRequest) => void;
  onBack: () => void;
}

const SCOPES: SearchScope[] = ['NEARBY', 'NEIGHBORHOOD', 'CITY'];

export function MatchFeedScreen({ controller, isAdmin, onOffer, onMyOffers, onBack }: Props) {
  return (
    <Screen title="Partidos para mi equipo" onBack={onBack}>
      <ChoiceChips
        label="Alcance"
        selected={[controller.scope]}
        choices={SCOPES.map((s) => ({ value: s, label: SCOPE_LABEL[s] }))}
        onToggle={(v) => controller.handleScope(v as SearchScope)}
      />
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(items) =>
          items.map((request) => (
            <Card
              key={request.id}
              title={request.team.name}
              subtitle={`${request.team.neighborhood} ${distanceText(request.distance_band)} · ${formatLocal(request.window_start)} → ${formatLocal(request.window_end)} · ${REFEREE_LABEL[request.referee_mode]} · ${PLACE_LABEL[request.place_kind]}`}
              badge={request.target_team_id ? 'Te retaron' : undefined}
            >
              {isAdmin ? <PrimaryButton label="Hacer oferta" onPress={() => onOffer(request)} /> : null}
              <PrimaryButton label="Ver mi oferta" variant="secondary" onPress={() => onMyOffers(request)} />
            </Card>
          ))
        }
      </StateView>
    </Screen>
  );
}
