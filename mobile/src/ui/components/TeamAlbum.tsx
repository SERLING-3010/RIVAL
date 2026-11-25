// Álbum del equipo (Sprint 23): se abre al tocar la barra; especiales en curso y las quince casillas.

import { StyleSheet, View } from 'react-native';

import type { TeamCard } from '../../domain/teamCardModels';
import { SpecialsAlbum } from './SpecialsAlbum';
import { SpecialsInProgress } from './SpecialsInProgress';

export function TeamAlbum({ card, media }: { card: TeamCard; media: number }) {
  return (
    <View style={styles.wrap}>
      <SpecialsInProgress
        media={media}
        specials={card.specials}
        note="Hazañas del equipo con resultados confirmados. Una especial ganada queda para siempre en el álbum."
      />
      <SpecialsAlbum specials={card.specials} title="ÁLBUM DEL EQUIPO" />
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { gap: 12 },
});
