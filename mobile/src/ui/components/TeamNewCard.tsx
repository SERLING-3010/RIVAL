// La carta del equipo que se revela al ganar una especial (Sprint 23): lámina, escudo y nombre.

import { StyleSheet, Text, View } from 'react-native';

import type { SpecialTier } from '../../domain/cardTiers';
import { TIERS } from '../../domain/cardTiers';
import { parseCrest } from '../../domain/teamLook';
import { TeamCrest } from './TeamCrest';
import { TierFoil } from './TierFoil';

interface Props {
  tier: SpecialTier;
  teamName: string;
  crest: string | null;
  media: number | null;
}

export function TeamNewCard({ tier, teamName, crest, media }: Props) {
  const ink = { color: TIERS[tier].ink };
  return (
    <View style={styles.size}>
      <TierFoil tier={tier} radius={22} style={styles.face}>
        <TeamCrest crest={parseCrest(crest)} teamName={teamName} size={72} />
        <Text style={[styles.name, ink]} numberOfLines={1}>
          {teamName.toUpperCase()}
        </Text>
        <Text style={[styles.label, ink]}>CARTA DEL EQUIPO · MEDIA {media ?? '–'}</Text>
      </TierFoil>
    </View>
  );
}

const styles = StyleSheet.create({
  size: { width: 230, height: 230 },
  face: { alignItems: 'center', justifyContent: 'center', gap: 10, padding: 16 },
  name: { fontSize: 24, fontWeight: '900', maxWidth: 200 },
  label: { fontSize: 11, fontWeight: '800', letterSpacing: 1 },
});
