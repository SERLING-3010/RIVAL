// Barra del equipo (Sprints 22 y 23): el diseño de siempre. El cuadro de la media lleva la lámina de su
// carta (bronce, plata, oro, rubí…). Mantener presionado el escudo o la media deja cambiarlos al DT.

import { Pressable, StyleSheet, Text, View } from 'react-native';

import { TIERS } from '../../domain/cardTiers';
import type { Squad } from '../../domain/squadModels';
import { parseCrest } from '../../domain/teamLook';
import { TeamCrest } from './TeamCrest';
import { TierFoil } from './TierFoil';

interface Props {
  squad: Squad;
  onToggleAlbum: () => void;
  onEditCrest: () => void;
  onChooseDesign: () => void;
}

export function SquadHeader({ squad, onToggleAlbum, onEditCrest, onChooseDesign }: Props) {
  const tier = squad.card?.display_tier ?? 'BRONCE';
  const look = TIERS[tier];
  const canChoose = squad.can_edit && (squad.card?.available.length ?? 0) > 1;
  const facts = [
    squad.formation,
    `récord ${squad.wins}-${squad.draws}-${squad.losses}`,
    squad.level === null ? 'sin nivel aún' : `nivel ${squad.level}`,
  ].filter(Boolean);
  return (
    <Pressable
      onPress={onToggleAlbum}
      accessibilityRole="button"
      accessibilityHint="Toca para ver el álbum de especiales del equipo."
      style={styles.panel}
    >
      <Pressable
        onLongPress={squad.can_edit ? onEditCrest : undefined}
        delayLongPress={450}
        accessibilityRole={squad.can_edit ? 'button' : undefined}
        accessibilityLabel={`Escudo de ${squad.team.name}`}
        accessibilityHint={squad.can_edit ? 'Mantén presionado para cambiar el escudo.' : undefined}
      >
        <TeamCrest crest={parseCrest(squad.crest)} teamName={squad.team.name} />
      </Pressable>
      <View style={styles.middle}>
        <Text style={styles.name} numberOfLines={1}>
          {squad.team.name}
        </Text>
        <Text style={styles.facts}>{facts.join(' · ')}</Text>
        <View style={styles.badges}>
          {squad.badges.slice(0, 2).map((b) => (
            <Text key={b} style={styles.badge}>
              {b}
            </Text>
          ))}
        </View>
      </View>
      <Pressable
        onLongPress={canChoose ? onChooseDesign : undefined}
        delayLongPress={450}
        accessibilityRole={canChoose ? 'button' : undefined}
        accessibilityLabel={`Media ${squad.media ?? 'sin dato'}, carta ${look.label}`}
        accessibilityHint={canChoose ? 'Mantén presionado para cambiar el diseño.' : undefined}
        style={styles.mediaBox}
      >
        <TierFoil tier={tier} radius={12} frameWidth={1.5} style={styles.media}>
          <Text style={[styles.mediaValue, { color: look.ink }]}>{squad.media ?? '–'}</Text>
          <Text style={[styles.mediaLabel, { color: look.ink }]}>MEDIA</Text>
        </TierFoil>
      </Pressable>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  panel: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    backgroundColor: '#0E2217',
    borderWidth: 1,
    borderColor: '#1D3A29',
    borderRadius: 16,
    padding: 12,
  },
  middle: { flex: 1, gap: 2 },
  name: { color: '#EAF5EE', fontSize: 22, fontWeight: '900' },
  facts: { color: '#9DB8A8', fontSize: 12 },
  badges: { flexDirection: 'row', gap: 4, marginTop: 2 },
  badge: {
    color: '#A6F0C2',
    fontSize: 10,
    fontWeight: '700',
    borderWidth: 1,
    borderColor: '#2BD46B',
    borderRadius: 999,
    paddingHorizontal: 7,
    paddingVertical: 2,
  },
  mediaBox: { width: 66, height: 62 },
  media: { alignItems: 'center', justifyContent: 'center' },
  mediaValue: { fontSize: 28, fontWeight: '900', lineHeight: 30 },
  mediaLabel: { fontSize: 9, fontWeight: '900', letterSpacing: 1 },
});
