// ¡Nueva carta! (Sprint 23): sobre sellado que se toca para revelar la especial recién ganada.
// Siempre sale la carta que se ganó jugando: no hay azar ni nada que comprar.

import type { ReactNode } from 'react';
import { useEffect, useRef, useState } from 'react';
import { Animated, Easing, Modal, Pressable, StyleSheet, Text, View } from 'react-native';
import Svg, { Path } from 'react-native-svg';

import type { SpecialTier } from '../../domain/cardTiers';
import { TIERS } from '../../domain/cardTiers';
import { Pulse } from './CardLoops';
import { PrimaryButton } from './PrimaryButton';
import { RevealRays } from './RevealRays';

interface Props {
  tier: SpecialTier | null;
  owner: string; // "tu carta" o "Chuchuwaza"
  children: ReactNode; // la carta ya revelada
  onDone: () => void;
}

export function NewCardReveal({ tier, owner, children, onDone }: Props) {
  const [open, setOpen] = useState(false);
  const pop = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    setOpen(false);
    pop.setValue(0);
  }, [pop, tier]);
  if (tier === null) return null;
  const look = TIERS[tier];
  const reveal = () => {
    setOpen(true);
    Animated.timing(pop, {
      toValue: 1,
      duration: 750,
      easing: Easing.out(Easing.back(1.4)),
      useNativeDriver: true,
    }).start();
  };
  const scale = pop.interpolate({ inputRange: [0, 1], outputRange: [0.4, 1] });
  const rotateY = pop.interpolate({ inputRange: [0, 1], outputRange: ['180deg', '0deg'] });
  return (
    <Modal visible animationType="fade" onRequestClose={onDone}>
      <View style={styles.screen}>
        <RevealRays color={look.swatch} />
        {open ? (
          <>
            <Text style={styles.title}>
              ¡NUEVA CARTA:{'\n'}
              {look.label.toUpperCase()}!
            </Text>
            <Animated.View style={{ transform: [{ perspective: 900 }, { scale }, { rotateY }] }}>
              {children}
            </Animated.View>
            <Text style={[styles.rarity, { color: look.swatch }]}>{look.rarity}</Text>
            <Text style={styles.meta}>Es {owner} para siempre, aunque la media baje.</Text>
            <View style={styles.button}>
              <PrimaryButton label="¡Vamos!" onPress={onDone} />
            </View>
          </>
        ) : (
          <>
            <Text style={styles.kicker}>¡SUBISTE DE CARTA!</Text>
            <Pressable
              onPress={reveal}
              accessibilityRole="button"
              accessibilityLabel="Revelar la carta nueva"
              style={[styles.sealed, { borderColor: look.swatch }]}
            >
              <Svg width={120} height={120} viewBox="0 0 76 76">
                <Path
                  d="M14 18 L34 38 L14 58"
                  fill="none"
                  stroke={look.swatch}
                  strokeWidth={7}
                  strokeLinecap="round"
                />
                <Path
                  d="M62 18 L42 38 L62 58"
                  fill="none"
                  stroke="#EAF5EE"
                  strokeWidth={7}
                  strokeLinecap="round"
                />
              </Svg>
              <Pulse duration={800} from={0.5} to={1}>
                <Text style={styles.tap}>Toca para revelar</Text>
              </Pulse>
            </Pressable>
            <Text style={styles.meta}>Siempre sale la carta que se ganó jugando: aquí no hay azar.</Text>
          </>
        )}
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: '#06120C',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 18,
    padding: 24,
    overflow: 'hidden',
  },
  kicker: { color: '#F6DE92', fontSize: 15, fontWeight: '900', letterSpacing: 2 },
  title: { color: '#EAF5EE', fontSize: 34, fontWeight: '900', fontStyle: 'italic', textAlign: 'center' },
  sealed: {
    width: 210,
    height: 300,
    borderRadius: 22,
    borderWidth: 3,
    backgroundColor: '#0E2217',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 24,
  },
  tap: { color: '#EAF5EE', fontSize: 15, fontWeight: '800' },
  rarity: { fontSize: 14, fontWeight: '900', letterSpacing: 2 },
  meta: { color: '#9DB8A8', fontSize: 14, textAlign: 'center', maxWidth: 300 },
  button: { alignSelf: 'stretch' },
});
