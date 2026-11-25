// Animaciones en bucle de la carta (Sprint 23): pulso de opacidad y desplazamiento lateral.
// Si el teléfono pide reducir movimiento quedan quietas, a medio camino.

import type { ReactNode } from 'react';
import { useEffect, useRef, useState } from 'react';
import type { StyleProp, ViewStyle } from 'react-native';
import { AccessibilityInfo, Animated, Easing } from 'react-native';

export function useReduceMotion(): boolean {
  const [reduce, setReduce] = useState(true);
  useEffect(() => {
    let alive = true;
    void AccessibilityInfo.isReduceMotionEnabled().then((value) => {
      if (alive) setReduce(value);
    });
    return () => {
      alive = false;
    };
  }, []);
  return reduce;
}

/** Va y vuelve de 0 a 1 sin parar. */
function useBounce(duration: number): Animated.Value {
  const value = useRef(new Animated.Value(0.5)).current;
  const reduce = useReduceMotion();
  useEffect(() => {
    if (reduce) return undefined;
    const ease = Easing.inOut(Easing.sin);
    const loop = Animated.loop(
      Animated.sequence([
        Animated.timing(value, { toValue: 1, duration, easing: ease, useNativeDriver: true }),
        Animated.timing(value, { toValue: 0, duration, easing: ease, useNativeDriver: true }),
      ]),
    );
    loop.start();
    return () => loop.stop();
  }, [duration, reduce, value]);
  return value;
}

interface LoopProps {
  duration: number;
  style?: StyleProp<ViewStyle>;
  children?: ReactNode;
}

/** Opacidad que late entre `from` y `to`. */
export function Pulse({ duration, from, to, style, children }: LoopProps & { from: number; to: number }) {
  const value = useBounce(duration);
  const opacity = value.interpolate({ inputRange: [0, 1], outputRange: [from, to] });
  return (
    <Animated.View pointerEvents="none" style={[style, { opacity }]}>
      {children}
    </Animated.View>
  );
}

/** Se desliza de lado a lado `range` puntos. */
export function Drift({ duration, range, style, children }: LoopProps & { range: number }) {
  const value = useBounce(duration);
  const translateX = value.interpolate({ inputRange: [0, 1], outputRange: [-range, range] });
  return (
    <Animated.View pointerEvents="none" style={[style, { transform: [{ translateX }] }]}>
      {children}
    </Animated.View>
  );
}
