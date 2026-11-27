// Emblema de los niveles más altos (Sprint 23): corona grabada (Corona) o símbolo RIVAL en neón (Élite).

import Svg, { Path } from 'react-native-svg';

import { Pulse } from './CardLoops';

export function TierEmblem({ kind, color }: { kind: 'crown' | 'neon'; color: string }) {
  if (kind === 'crown') {
    return (
      <Svg width={120} height={76} viewBox="0 0 64 40" accessibilityLabel="Corona">
        <Path
          d="M6 34 L12 10 L24 24 L32 4 L40 24 L52 10 L58 34 Z"
          fill="none"
          stroke={color}
          strokeWidth={2.4}
          strokeLinejoin="round"
        />
        <Path d="M6 38 H58" stroke={color} strokeWidth={2.4} />
      </Svg>
    );
  }
  return (
    <Pulse duration={1200} from={0.55} to={1}>
      <Svg width={150} height={150} viewBox="0 0 76 76" accessibilityLabel="Símbolo de RIVAL en neón">
        <Path
          d="M14 18 L34 38 L14 58"
          fill="none"
          stroke="#2BD46B"
          strokeWidth={5}
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <Path
          d="M62 18 L42 38 L62 58"
          fill="none"
          stroke="#7BE8A4"
          strokeWidth={5}
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </Svg>
    </Pulse>
  );
}
