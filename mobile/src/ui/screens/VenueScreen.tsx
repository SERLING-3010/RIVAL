// Detalle de un establecimiento. Con un partido por reservar, muestra solo las franjas que lo cubren.

import { StyleSheet, Text } from 'react-native';

import type { VenueController } from '../../controllers/useVenues';
import { formatLocal } from '../../domain/dateTime';
import type { Sport } from '../../domain/models';
import type { MatchToBook } from '../../domain/venueModels';
import { formatPesos, slotCoversMatch } from '../../domain/venueRules';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { VenueOwnerPanel } from '../components/VenueOwnerPanel';
import { colors, font } from '../theme';

interface Props {
  controller: VenueController;
  sports: Sport[];
  match: MatchToBook | null;
  onBooked: () => void;
  onBack: () => void;
}

export function VenueScreen({ controller, sports, match, onBooked, onBack }: Props) {
  const busy = controller.action.busy;
  return (
    <Screen title="Establecimiento" onBack={onBack}>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(detail) => {
          const v = detail.venue;
          const slots = match
            ? detail.slots.filter(
                (s) =>
                  s.sport_code === match.sportCode &&
                  slotCoversMatch(s, match.kickoffAt, match.durationMinutes),
              )
            : detail.slots;
          return (
            <>
              <Text style={styles.title}>{v.name}</Text>
              <Text style={styles.line}>
                {v.address} · {v.neighborhood}, {v.city}
              </Text>
              {v.reference_price ? (
                <Text style={styles.meta}>
                  Tarifa de referencia: {formatPesos(v.reference_price)} por hora. Se paga en el
                  establecimiento.
                </Text>
              ) : null}
              <Card title={`Canchas (${detail.courts.length})`}>
                {detail.courts.map((c) => (
                  <Text key={c.id} style={styles.line}>
                    {c.name} · {c.sport_code}
                    {c.surface ? ` · ${c.surface}` : ''}
                  </Text>
                ))}
              </Card>
              <Card title={match ? 'Franjas libres para tu partido' : `Franjas libres (${slots.length})`}>
                {slots.length === 0 ? (
                  <Text style={styles.meta}>
                    No hay franjas libres{match ? ' que cubran tu partido' : ''}.
                  </Text>
                ) : null}
                {slots.map((s) => (
                  <Card
                    key={s.id}
                    title={`${formatLocal(s.starts_at)} – ${formatLocal(s.ends_at)}`}
                    subtitle={s.court_name}
                  >
                    {match ? (
                      <PrimaryButton
                        label="Reservar esta franja"
                        disabled={busy}
                        onPress={() => void controller.handleBook(match.contractId, s.id, onBooked)}
                      />
                    ) : null}
                  </Card>
                ))}
              </Card>
              {detail.is_owner ? (
                <VenueOwnerPanel detail={detail} sports={sports} controller={controller} />
              ) : null}
            </>
          );
        }}
      </StateView>
      {controller.action.message ? (
        <Text style={styles.line} accessibilityLiveRegion="polite">
          {controller.action.message}
        </Text>
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  title: { color: colors.text, fontSize: font.heading, fontWeight: '700' },
  line: { color: colors.text, fontSize: font.small },
  meta: { color: colors.textMuted, fontSize: font.small },
});
