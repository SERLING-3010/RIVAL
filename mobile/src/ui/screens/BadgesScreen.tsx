// Insignias ganadas (con su fecha) y las que faltan (con su avance). Nada se compra ni se regala.

import { StyleSheet, Text } from 'react-native';

import type { Loader } from '../../controllers/useLoader';
import type { Badge } from '../../domain/badgeModels';
import { splitBadges } from '../../domain/badgeModels';
import { formatLocal } from '../../domain/dateTime';
import { Card } from '../components/Card';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { colors, font } from '../theme';

interface Props {
  title: string;
  controller: Loader<Badge[]>;
  onBack: () => void;
}

export function BadgesScreen({ title, controller, onBack }: Props) {
  return (
    <Screen title={title} onBack={onBack}>
      <Text style={styles.meta}>Se ganan jugando: solo cuentan partidos con resultado confirmado.</Text>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(badges) => {
          const { earned, pending } = splitBadges(badges);
          return (
            <>
              <Text style={styles.heading}>Ganadas ({earned.length})</Text>
              {earned.length === 0 ? <Text style={styles.meta}>Todavía ninguna.</Text> : null}
              {earned.map((b) => (
                <Card
                  key={b.code}
                  title={b.name}
                  subtitle={b.description}
                  badge={formatLocal(b.earned_at ?? '')}
                />
              ))}
              <Text style={styles.heading}>Por ganar ({pending.length})</Text>
              {pending.map((b) => (
                <Card key={b.code} title={b.name} subtitle={b.description} badge={b.progress ?? undefined} />
              ))}
            </>
          );
        }}
      </StateView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  heading: { color: colors.text, fontSize: font.heading, fontWeight: '700' },
  meta: { color: colors.textMuted, fontSize: font.small },
});
