// La carta del jugador: se voltea al tocarla (giro 3D) para mostrar la ficha completa.

import { useRef, useState } from 'react';
import { Animated, Easing, Pressable, StyleSheet } from 'react-native';

import { faceFromPlayer } from '../../domain/cardModels';
import type { PlayerCard } from '../../domain/managerModels';
import { CardBack } from './CardBack';
import { CardFront } from './CardFront';

export function PlayerCardFoil({ player }: { player: PlayerCard }) {
  const turn = useRef(new Animated.Value(0)).current;
  const [flipped, setFlipped] = useState(false);
  const flip = () => {
    // Sin rebote: termina justo en su lugar y el texto queda nítido al instante.
    Animated.timing(turn, {
      toValue: flipped ? 0 : 1,
      duration: 450,
      easing: Easing.out(Easing.cubic),
      useNativeDriver: true,
    }).start();
    setFlipped(!flipped);
  };
  const front = turn.interpolate({ inputRange: [0, 1], outputRange: ['0deg', '180deg'] });
  const back = turn.interpolate({ inputRange: [0, 1], outputRange: ['180deg', '360deg'] });
  return (
    <Pressable
      onPress={flip}
      accessibilityRole="button"
      accessibilityLabel={
        flipped
          ? 'Ficha completa. Toca para ver el frente de la carta.'
          : `Carta de ${player.display_name}, media ${player.card.media}. Toca para ver la ficha completa.`
      }
      style={styles.card}
    >
      <Animated.View style={[styles.side, { transform: [{ perspective: 1200 }, { rotateY: front }] }]}>
        <CardFront face={faceFromPlayer(player)} />
      </Animated.View>
      <Animated.View style={[styles.side, { transform: [{ perspective: 1200 }, { rotateY: back }] }]}>
        <CardBack player={player} />
      </Animated.View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: { alignSelf: 'center', width: 270, height: 392 },
  side: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backfaceVisibility: 'hidden' },
});
