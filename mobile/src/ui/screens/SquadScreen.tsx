// Equipo en modo juego (Sprints 22 y 23): barra del equipo con su lámina, Titulares, Jugadores y Comparar.
// Solo la ven los miembros del equipo: incluye la alineación, que el rival no debe ver.

import { useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import type { SquadController } from '../../controllers/useSquad';
import { CompareView } from '../components/CompareView';
import { PitchView } from '../components/PitchView';
import { Screen } from '../components/Screen';
import { SquadGrid } from '../components/SquadGrid';
import { SquadHeader } from '../components/SquadHeader';
import { StateView } from '../components/StateView';
import { TeamAlbum } from '../components/TeamAlbum';
import { TeamLookSheets } from '../components/TeamLookSheets';
import { MIN_TOUCH } from '../theme';

type Tab = 'pitch' | 'players' | 'compare';

interface Props {
  controller: SquadController;
  onOpenCard: (userId: number) => void;
  onBack: () => void;
}

export function SquadScreen({ controller, onOpenCard, onBack }: Props) {
  const [tab, setTab] = useState<Tab>('pitch');
  const [album, setAlbum] = useState(false);
  const [sheet, setSheet] = useState<'crest' | 'design' | null>(null);
  return (
    <Screen title="Plantilla" tone="dark" onBack={onBack}>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(squad) => {
          const tabs: [Tab, string][] = [
            ['pitch', 'Titulares'],
            ['players', `Jugadores (${squad.members.length})`],
            ['compare', 'Comparar'],
          ];
          return (
            <>
              <SquadHeader
                squad={squad}
                onToggleAlbum={() => setAlbum((a) => !a)}
                onEditCrest={() => setSheet('crest')}
                onChooseDesign={() => setSheet('design')}
              />
              <TeamLookSheets
                squad={squad}
                sheet={sheet}
                controller={controller}
                onClose={() => setSheet(null)}
              />
              {album && squad.card && squad.media !== null ? (
                <TeamAlbum card={squad.card} media={squad.media} />
              ) : null}
              <View style={styles.tabs} accessibilityRole="tablist">
                {tabs.map(([key, label]) => (
                  <Pressable
                    key={key}
                    onPress={() => setTab(key)}
                    accessibilityRole="tab"
                    accessibilityState={{ selected: tab === key }}
                    style={[styles.tab, tab === key ? styles.tabOn : null]}
                  >
                    <Text style={[styles.tabText, tab === key ? styles.tabTextOn : null]}>{label}</Text>
                  </Pressable>
                ))}
              </View>
              {tab === 'pitch' ? <PitchView squad={squad} onOpen={onOpenCard} /> : null}
              {tab === 'players' ? (
                <SquadGrid members={squad.members} teamName={squad.team.name} onOpen={onOpenCard} />
              ) : null}
              {tab === 'compare' ? (
                <>
                  <Text style={styles.hint}>Elige dos jugadores para compararlos.</Text>
                  <View style={styles.picks}>
                    {squad.members.map((m) => {
                      const on = controller.picked.includes(m.user_id);
                      return (
                        <Pressable
                          key={m.user_id}
                          onPress={() => controller.handlePick(m.user_id)}
                          accessibilityRole="checkbox"
                          accessibilityState={{ checked: on }}
                          style={[styles.pick, on ? styles.pickOn : null]}
                        >
                          <Text style={[styles.pickText, on ? styles.pickTextOn : null]}>
                            {m.media} {m.display_name}
                          </Text>
                        </Pressable>
                      );
                    })}
                  </View>
                  {controller.compare ? (
                    <StateView state={controller.compare.state} onRetry={controller.compare.handleReload}>
                      {(pair) => <CompareView pair={pair} />}
                    </StateView>
                  ) : null}
                </>
              ) : null}
            </>
          );
        }}
      </StateView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  tabs: { flexDirection: 'row', backgroundColor: '#0E2217', borderRadius: 12, padding: 3, gap: 3 },
  tab: { flex: 1, minHeight: MIN_TOUCH, borderRadius: 9, alignItems: 'center', justifyContent: 'center' },
  tabOn: { backgroundColor: '#2BD46B' },
  tabText: { color: '#EAF5EE', fontSize: 13, fontWeight: '700' },
  tabTextOn: { color: '#06120C', fontWeight: '900' },
  hint: { color: '#9DB8A8', fontSize: 13 },
  picks: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  pick: {
    minHeight: MIN_TOUCH,
    paddingHorizontal: 12,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#1D3A29',
    justifyContent: 'center',
  },
  pickOn: { borderColor: '#2BD46B', backgroundColor: '#123A25' },
  pickText: { color: '#EAF5EE', fontSize: 13, fontWeight: '600' },
  pickTextOn: { color: '#A6F0C2', fontWeight: '800' },
});
