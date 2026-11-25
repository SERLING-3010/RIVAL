// Capas propias de cada nivel (Sprint 23): segunda lámina, tornasol, aurora, brillo, destellos y borde que late.

import { LinearGradient } from 'expo-linear-gradient';
import { StyleSheet, View } from 'react-native';

import type { TierLook } from '../../domain/cardTiers';
import { CardSheen } from './CardSheen';
import { Drift, Pulse } from './CardLoops';

const FILL = { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0 } as const;
const STARS: [string, string, number][] = [
  ['20%', '18%', 4],
  ['72%', '12%', 3],
  ['84%', '46%', 5],
  ['30%', '52%', 3],
  ['58%', '34%', 4],
  ['12%', '40%', 3],
  ['66%', '62%', 3],
];
const HOLO = [
  'rgba(255,122,217,0)',
  'rgba(255,122,217,0.5)',
  'rgba(122,224,255,0.5)',
  'rgba(182,255,122,0.5)',
  'rgba(255,226,122,0)',
] as const;
const AURORA = [
  'rgba(43,212,107,0)',
  'rgba(43,212,107,0.75)',
  'rgba(122,224,255,0.55)',
  'rgba(199,125,255,0.45)',
  'rgba(199,125,255,0)',
] as const;

/** Lo que va debajo del texto de la carta, en el orden en que se apila. */
export function TierEffects({ look }: { look: TierLook }) {
  return (
    <>
      {look.shift ? (
        <Pulse duration={2600} from={0} to={1} style={FILL}>
          <LinearGradient
            colors={look.shift}
            locations={[0, 0.28, 0.48, 0.72, 1]}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={StyleSheet.absoluteFill}
          />
        </Pulse>
      ) : null}
      {look.aurora ? (
        <Drift duration={3600} range={50} style={styles.aurora}>
          <LinearGradient
            colors={AURORA}
            start={{ x: 0, y: 0.3 }}
            end={{ x: 1, y: 0.7 }}
            style={styles.auroraBand}
          />
        </Drift>
      ) : null}
      {look.holo ? (
        <Drift duration={1800} range={140} style={styles.holo}>
          <LinearGradient
            colors={HOLO}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={StyleSheet.absoluteFill}
          />
        </Drift>
      ) : null}
      {look.sheen ? <CardSheen /> : null}
      {look.stars ? (
        <Pulse duration={1100} from={0.15} to={1} style={FILL}>
          {STARS.map(([left, top, size]) => (
            <View
              key={`${left}-${top}`}
              style={[
                styles.star,
                {
                  left,
                  top,
                  width: size,
                  height: size,
                  borderRadius: size / 2,
                  backgroundColor: look.stars ?? '#FFFFFF',
                },
              ]}
            />
          ))}
        </Pulse>
      ) : null}
      {look.glow ? (
        <Pulse duration={1300} from={0.25} to={0.85} style={[styles.glow, { borderColor: look.glow }]} />
      ) : null}
    </>
  );
}

const styles = StyleSheet.create({
  aurora: { position: 'absolute', left: -60, right: -60, top: 10, height: 210 },
  auroraBand: { flex: 1, borderRadius: 120, opacity: 0.8 },
  holo: { position: 'absolute', top: 0, bottom: 0, left: -40, width: 340, opacity: 0.45 },
  star: { position: 'absolute' },
  glow: { ...FILL, borderRadius: 22, borderWidth: 6 },
});
