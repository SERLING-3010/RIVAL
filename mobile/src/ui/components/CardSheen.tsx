// Brillo que recorre la lámina metálica. No se anima si el teléfono pide reducir movimiento.

import { LinearGradient } from 'expo-linear-gradient';
import { useEffect, useRef, useState } from 'react';
import { AccessibilityInfo, Animated, Easing, StyleSheet } from 'react-native';

export function CardSheen() {
  const progress = useRef(new Animated.Value(0)).current;
  const [reduceMotion, setReduceMotion] = useState(true);

  useEffect(() => {
    let alive = true;
    void AccessibilityInfo.isReduceMotionEnabled().then((reduce) => {
      if (alive) setReduceMotion(reduce);
    });
    return () => {
      alive = false;
    };
  }, []);

  useEffect(() => {
    if (reduceMotion) return undefined;
    const loop = Animated.loop(
      Animated.sequence([
        Animated.timing(progress, {
          toValue: 1,
          duration: 2000,
          easing: Easing.inOut(Easing.quad),
          useNativeDriver: true,
        }),
        Animated.delay(1600),
        Animated.timing(progress, { toValue: 0, duration: 0, useNativeDriver: true }),
      ]),
    );
    loop.start();
    return () => loop.stop();
  }, [progress, reduceMotion]);

  if (reduceMotion) return null;
  const translateX = progress.interpolate({ inputRange: [0, 1], outputRange: [-180, 320] });
  return (
    <Animated.View
      pointerEvents="none"
      style={[styles.band, { transform: [{ translateX }, { rotate: '18deg' }] }]}
    >
      <LinearGradient
        colors={['rgba(255,255,255,0)', 'rgba(255,255,255,0.55)', 'rgba(255,255,255,0)']}
        start={{ x: 0, y: 0.5 }}
        end={{ x: 1, y: 0.5 }}
        style={StyleSheet.absoluteFill}
      />
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  band: { position: 'absolute', top: -80, left: 0, width: 110, height: 560 },
});
