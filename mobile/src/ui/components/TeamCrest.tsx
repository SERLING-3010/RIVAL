// Escudo del equipo (Sprint 23): forma, dos colores y símbolo de RIVAL. Sin escudo guardado, el de siempre.

import { StyleSheet, Text, View } from 'react-native';
import Svg, { Circle, Path } from 'react-native-svg';

import { initials } from '../../domain/cardModels';
import type { Crest, CrestShape, CrestSymbol } from '../../domain/teamLook';

const SHAPE_PATH: Record<CrestShape, string> = {
  ESCUDO: 'M6 4 H42 V24 C42 36 33 43 24 46 C15 43 6 36 6 24 Z',
  CIRCULO: 'M24 2 A22 22 0 1 1 23.9 2 Z',
  ROMBO: 'M24 2 L46 24 L24 46 L2 24 Z',
  BANDERA: 'M4 6 H44 V36 L24 46 L4 36 Z',
};

const SYMBOL_PATH: Record<Exclude<CrestSymbol, 'INICIALES' | 'BALON'>, string> = {
  ESTRELLA: 'M24 11 L27.5 20 L37 20.5 L29.5 26.5 L32 36 L24 30.5 L16 36 L18.5 26.5 L11 20.5 L20.5 20 Z',
  RAYO: 'M27 9 L15 27 H23 L20 39 L33 20 H25 Z',
  CORONA: 'M12 33 L14 17 L20 24 L24 13 L28 24 L34 17 L36 33 Z',
};

interface Props {
  crest: Crest | null;
  teamName: string;
  size?: number;
}

export function TeamCrest({ crest, teamName, size = 48 }: Props) {
  if (crest === null) {
    // El predeterminado: cuadro verde redondeado con las iniciales, como siempre.
    return (
      <View style={[styles.square, { width: size, height: size, borderRadius: size * 0.3 }]}>
        <Text style={[styles.letters, { fontSize: size * 0.38 }]}>{initials(teamName)}</Text>
      </View>
    );
  }
  const { shape, primary, secondary, symbol } = crest;
  return (
    <View style={{ width: size, height: size }} accessibilityLabel={`Escudo de ${teamName}`}>
      <Svg width={size} height={size} viewBox="0 0 48 48">
        <Path
          d={SHAPE_PATH[shape]}
          fill={primary}
          stroke={secondary}
          strokeWidth={2.5}
          strokeLinejoin="round"
        />
        {symbol === 'BALON' ? (
          <>
            <Circle cx={24} cy={24} r={10} fill="none" stroke={secondary} strokeWidth={2.5} />
            <Path d="M24 18 L29 21.5 L27 27.5 H21 L19 21.5 Z" fill={secondary} />
          </>
        ) : symbol !== 'INICIALES' ? (
          <Path d={SYMBOL_PATH[symbol]} fill={secondary} />
        ) : null}
      </Svg>
      {symbol === 'INICIALES' ? (
        <View style={[StyleSheet.absoluteFill, styles.center]}>
          <Text style={[styles.letters, { color: secondary, fontSize: size * 0.3 }]}>
            {initials(teamName)}
          </Text>
        </View>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  square: { backgroundColor: '#0B6B3A', alignItems: 'center', justifyContent: 'center' },
  center: { alignItems: 'center', justifyContent: 'center' },
  letters: { color: '#FFFFFF', fontWeight: '900' },
});
