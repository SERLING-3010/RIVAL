// Rayos que giran detrás de la carta nueva (Sprint 23). Quietos si el teléfono pide reducir movimiento.

import { useEffect, useRef } from 'react';
import { Animated, Easing, StyleSheet, View } from 'react-native';

import { useReduceMotion } from './CardLoops';

const RAYS = 14;
const SIZE = 760;

export function RevealRays({ color }: { color: string }) {
  const spin = useRef(new Animated.Value(0)).current;
  const reduce = useReduceMotion();
  useEffect(() => {
    if (reduce) return undefined;
    const loop = Animated.loop(
      Animated.timing(spin, { toValue: 1, duration: 18000, easing: Easing.linear, useNativeDriver: true }),
    );
    loop.start();
    return () => loop.stop();
  }, [reduce, spin]);
  const rotate = spin.interpolate({ inputRange: [0, 1], outputRange: ['0deg', '360deg'] });
  return (
    <View pointerEvents="none" style={styles.center}>
      <Animated.View style={[styles.wheel, { transform: [{ rotate }] }]}>
        {Array.from({ length: RAYS }, (_, i) => (
          <View
            key={i}
            style={[
              styles.ray,
              { backgroundColor: color, transform: [{ rotate: `${(360 / RAYS) * i}deg` }] },
            ]}
          />
        ))}
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  center: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    alignItems: 'center',
    justifyContent: 'center',
  },
  wheel: { width: SIZE, height: SIZE, alignItems: 'center', justifyContent: 'center', opacity: 0.18 },
  ray: { position: 'absolute', width: 34, height: SIZE },
});
