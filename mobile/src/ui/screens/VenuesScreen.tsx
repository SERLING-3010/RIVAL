// Lista de establecimientos: los míos (dueño) o los que sirven para un partido (DT).

import { StyleSheet, Text } from 'react-native';

import type { Loader } from '../../controllers/useLoader';
import type { VenueSummary } from '../../domain/venueModels';
import { formatPesos } from '../../domain/venueRules';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { colors, font } from '../theme';

interface Props {
  title: string;
  lead: string;
  controller: Loader<VenueSummary[]>;
  onOpen: (venueId: number) => void;
  onCreate?: () => void;
  onBack: () => void;
}

export function VenuesScreen({ title, lead, controller, onOpen, onCreate, onBack }: Props) {
  return (
    <Screen title={title} onBack={onBack}>
      <Text style={styles.meta}>{lead}</Text>
      {onCreate ? <PrimaryButton label="Registrar establecimiento" onPress={onCreate} /> : null}
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(items) =>
          items.map((venue) => (
            <Card
              key={venue.id}
              title={venue.name}
              subtitle={`${venue.address} · ${venue.neighborhood}, ${venue.city}`}
              badge={venue.reference_price ? `${formatPesos(venue.reference_price)} / hora` : undefined}
              onPress={() => onOpen(venue.id)}
            />
          ))
        }
      </StateView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  meta: { color: colors.textMuted, fontSize: font.small },
});
