import { StyleSheet, Text } from 'react-native';

import type { LeagueHomeController } from '../../controllers/useLeagues';
import type { LeagueSummary } from '../../domain/leagueModels';
import { RELATION_LABEL } from '../../domain/leagueRules';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { TextField } from '../components/TextField';
import { colors, font } from '../theme';

interface Props {
  controller: LeagueHomeController;
  canCreate: boolean;
  onOpen: (leagueId: number) => void;
  onCreate: () => void;
  onBack: () => void;
}

const subtitle = (l: LeagueSummary) =>
  `${l.modality_code} · ${l.city} · Temporada ${l.season} · ${l.team_count} equipos · ${l.referee_count} árbitros`;

export function LeaguesScreen({ controller, canCreate, onOpen, onCreate, onBack }: Props) {
  return (
    <Screen title="Ligas" onBack={onBack}>
      <Text style={styles.section} accessibilityRole="header">
        Mis ligas
      </Text>
      <StateView state={controller.mine.state} onRetry={controller.mine.handleReload}>
        {(items) =>
          items.map((item) => (
            <Card
              key={item.league.id}
              title={item.league.name}
              subtitle={subtitle(item.league)}
              badge={RELATION_LABEL[item.relation]}
              onPress={() => onOpen(item.league.id)}
            />
          ))
        }
      </StateView>
      {canCreate ? <PrimaryButton label="Crear liga" onPress={onCreate} /> : null}
      <Text style={styles.section} accessibilityRole="header">
        Buscar ligas
      </Text>
      <TextField label="Nombre de la liga" value={controller.query} onChangeText={controller.handleQuery} />
      <PrimaryButton label="Buscar" variant="secondary" onPress={controller.handleSearch} />
      <StateView state={controller.results.state} onRetry={controller.results.handleReload}>
        {(page) =>
          page.items.map((league) => (
            <Card
              key={league.id}
              title={league.name}
              subtitle={subtitle(league)}
              onPress={() => onOpen(league.id)}
            />
          ))
        }
      </StateView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  section: { color: colors.text, fontSize: font.heading, fontWeight: '700' },
});
