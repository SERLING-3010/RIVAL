// Lámina del nivel (Sprint 23): degradado, marco y efectos. La usan el frente y el reverso de la carta,
// para que las dos caras tengan el mismo diseño (bronce con bronce, Élite con Élite…).

import { LinearGradient } from 'expo-linear-gradient';
import type { ReactNode } from 'react';
import type { StyleProp, ViewStyle } from 'react-native';
import { StyleSheet } from 'react-native';

import type { CardTier } from '../../domain/cardTiers';
import { TIERS } from '../../domain/cardTiers';
import { TierEffects } from './TierEffects';

/** Sobre tinta oscura, sombras oscuras; sobre tinta clara, sombras claras. */
export function shade(ink: string, alpha: number): string {
  const n = parseInt(ink.slice(1), 16);
  const light = ((n >> 16) & 255) * 0.299 + ((n >> 8) & 255) * 0.587 + (n & 255) * 0.114 > 128;
  return light ? `rgba(255,255,255,${alpha})` : `rgba(26,18,6,${alpha})`;
}

interface Props {
  tier: CardTier;
  radius: number;
  frameWidth?: number;
  style?: StyleProp<ViewStyle>;
  children?: ReactNode;
}

export function TierFoil({ tier, radius, frameWidth = 3, style, children }: Props) {
  const look = TIERS[tier];
  return (
    <LinearGradient
      colors={look.foil}
      locations={[0, 0.28, 0.48, 0.72, 1]}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={[
        styles.face,
        { borderRadius: radius },
        look.frame ? { borderWidth: frameWidth, borderColor: look.frame } : null,
        style,
      ]}
    >
      <TierEffects look={look} />
      {children}
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  face: { flex: 1, overflow: 'hidden', backfaceVisibility: 'hidden' },
});
