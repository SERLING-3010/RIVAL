// La misma carta de la ficha, a escala. Tocarla la voltea ahí mismo; mantenerla presionada abre la ficha.

import { useRef, useState } from 'react';
import { Animated, Easing, Pressable, StyleSheet, Text, View } from 'react-native';

import type { SquadCard } from '../../domain/squadModels';
import { roleMark, squadFace } from '../../domain/squadModels';
import { CardFront } from './CardFront';
import { MiniCardBack } from './MiniCardBack';
import { CARD_H, CARD_W, ScaledCard } from './ScaledCard';

export const MINI_W = 78;
const MINI_H = (CARD_H / CARD_W) * MINI_W;

interface Props {
  card: SquadCard;
  teamName: string;
  tag?: string | null; // posición en la alineación, encima de la carta (Sprint 23: la C o DT va dentro)
  onOpen: (userId: number) => void;
}

export function MiniCard({ card, teamName, tag, onOpen }: Props) {
  const turn = useRef(new Animated.Value(0)).current;
  const [flipped, setFlipped] = useState(false);
  const mark = roleMark(card.role);
  const flip = () => {
    // Duración fija y sin rebote: termina justo en 0° o 180°. Con resorte quedaba oscilando
    // unos milisegundos y iOS dibujaba borroso el texto pequeño hasta que se detenía.
    Animated.timing(turn, {
      toValue: flipped ? 0 : 1,
      duration: 380,
      easing: Easing.out(Easing.cubic),
      useNativeDriver: true,
    }).start();
    setFlipped(!flipped);
  };
  const front = turn.interpolate({ inputRange: [0, 1], outputRange: ['0deg', '180deg'] });
  const back = turn.interpolate({ inputRange: [0, 1], outputRange: ['180deg', '360deg'] });
  const who = `${card.display_name}, media ${card.media}${mark ? `, ${mark === 'C' ? 'capitán' : 'DT'}` : ''}`;
  return (
    <View style={styles.wrap}>
      {tag ? <Text style={styles.tag}>{tag.slice(0, 10)}</Text> : null}
      <Pressable
        onPress={flip}
        onLongPress={() => onOpen(card.user_id)}
        delayLongPress={450}
        accessibilityRole="button"
        accessibilityLabel={flipped ? `${who}. Reverso` : who}
        accessibilityHint="Toca para voltear la carta. Mantén presionado para abrir la ficha del jugador."
        accessibilityActions={[{ name: 'longpress', label: 'Abrir la ficha del jugador' }]}
        onAccessibilityAction={() => onOpen(card.user_id)}
        style={styles.card}
      >
        <Animated.View style={[styles.side, { transform: [{ perspective: 600 }, { rotateY: front }] }]}>
          <ScaledCard width={MINI_W}>
            <CardFront face={squadFace(card, teamName)} />
          </ScaledCard>
          {mark ? (
            <View style={styles.mark}>
              <Text style={styles.markText}>{mark}</Text>
            </View>
          ) : null}
        </Animated.View>
        <Animated.View style={[styles.side, { transform: [{ perspective: 600 }, { rotateY: back }] }]}>
          <MiniCardBack card={card} />
        </Animated.View>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { alignItems: 'center', gap: 3 },
  tag: {
    color: '#EAF5EE',
    backgroundColor: '#06120C',
    fontSize: 9,
    fontWeight: '800',
    borderRadius: 5,
    paddingHorizontal: 5,
    paddingVertical: 1,
    overflow: 'hidden',
  },
  // Capitán o DT: insignia pequeña dentro de la carta, en la esquina superior derecha.
  mark: {
    position: 'absolute',
    top: 4,
    right: 4,
    width: 14,
    height: 14,
    borderRadius: 7,
    backgroundColor: '#F6DE92',
    borderWidth: 1,
    borderColor: '#06120C',
    alignItems: 'center',
    justifyContent: 'center',
  },
  markText: { color: '#06120C', fontSize: 8, fontWeight: '900' },
  card: { width: MINI_W, height: MINI_H },
  side: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backfaceVisibility: 'hidden' },
});
