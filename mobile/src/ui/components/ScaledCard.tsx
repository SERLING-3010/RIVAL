// Dibuja la carta grande de la ficha (270 × 392) a escala, para que la plantilla muestre la misma carta.

import type { ReactNode } from 'react';
import { StyleSheet, View } from 'react-native';

export const CARD_W = 270;
export const CARD_H = 392;

export function ScaledCard({ width, children }: { width: number; children: ReactNode }) {
  const scale = width / CARD_W;
  const height = CARD_H * scale;
  return (
    <View style={[styles.box, { width, height }]}>
      <View
        style={[
          styles.full,
          {
            left: (width - CARD_W) / 2,
            top: (height - CARD_H) / 2,
            transform: [{ scale }],
          },
        ]}
      >
        {children}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  box: { overflow: 'hidden', borderRadius: 7 },
  full: { position: 'absolute', width: CARD_W, height: CARD_H },
});
