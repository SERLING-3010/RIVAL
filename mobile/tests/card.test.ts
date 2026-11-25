// Pruebas de la carta del jugador. Ejecutar: node --experimental-strip-types --test tests/
import assert from 'node:assert/strict';
import { test } from 'node:test';

import type { SpecialCard } from '../src/domain/cardModels.ts';
import {
  faceFromPlayer,
  frontStats,
  goalsPerMatch,
  initials,
  nextTierText,
} from '../src/domain/cardModels.ts';
import { albumTiles, coinsText, nextSpecials, tierProgress } from '../src/domain/cardProgress.ts';
import { SPECIAL_CODES, TIER_LABEL, TIERS } from '../src/domain/cardTiers.ts';
import type { PlayerCard } from '../src/domain/managerModels.ts';

const specials = (): SpecialCard[] =>
  SPECIAL_CODES.map((code) => ({
    code,
    min_media: TIERS[code].media,
    earned_at: code === 'RUBI' ? '2026-11-25T12:00:00Z' : null,
    goals: [{ label: 'hazaña', current: code === 'ESMERALDA' ? 2 : 0, target: 3 }],
  }));

const player = (over: Partial<PlayerCard> = {}): PlayerCard => ({
  user_id: 1,
  display_name: 'Andrés Mejía',
  position: 'Delantero',
  sports: ['FOOTBALL'],
  teams: [],
  matches: 24,
  goals: 18,
  wins: 14,
  draws: 4,
  losses: 6,
  rating_average: 8.1,
  rating_votes: 19,
  card: {
    media: 77,
    tier: 'ORO',
    next_tier: 'ORO_BRILLANTE',
    media_to_next: 3,
    display_tier: 'RUBI',
    market_value: 480,
    specials: specials(),
    hat_tricks: 2,
    check_ins: 5,
    recent: ['W', 'W', 'D', 'L', 'W'],
    badges: ['Debut', 'Goleador'],
  },
  ...over,
});

test('initials: dos letras o una, nunca vacío', () => {
  assert.equal(initials('Chuchuwaza'), 'C');
  assert.equal(initials('Rivales de Prueba'), 'RP');
  assert.equal(initials('   '), '?');
});

test('frontStats: las seis estadísticas reales en orden', () => {
  assert.deepEqual(
    frontStats(player()).map((s) => `${s.value} ${s.label}`),
    ['24 PJ', '14 VIC', '18 GOL', '8,1 VAL', '2 TRI', '2 INS'],
  );
  assert.equal(frontStats(player({ rating_average: null }))[3]?.value, '–');
});

test('la carta se dibuja con su mejor especial; la básica sale de la media', () => {
  assert.equal(faceFromPlayer(player()).tier, 'RUBI');
  const c = player().card;
  assert.equal(nextTierText(c), 'Faltan 3 de media para Oro brillante');
  assert.equal(nextTierText({ ...c, media_to_next: 1 }), 'Falta 1 de media para Oro brillante');
  assert.equal(
    nextTierText({ ...c, tier: 'ORO_BRILLANTE', next_tier: null, media_to_next: 0 }),
    'Carta básica máxima: Oro brillante',
  );
  assert.equal(TIER_LABEL.ORO, 'Oro común');
  assert.deepEqual(
    [TIERS.BRONCE.media, TIERS.PLATA.media, TIERS.ORO.media, TIERS.ORO_BRILLANTE.media],
    [0, 65, 75, 80],
  );
});

test('avance de la básica, especiales más cercanas y álbum', () => {
  const c = player().card; // media 77 entre Oro común (75) y Oro brillante (80)
  assert.equal(tierProgress(c), 0.4);
  assert.equal(tierProgress({ ...c, next_tier: null }), 1);
  const next = nextSpecials(c);
  assert.equal(next.length, 3);
  assert.equal(next[0]?.code, 'ESMERALDA'); // la más cercana: media 75 cumplida y 2 de 3
  assert.ok(next.every((s) => s.code !== 'RUBI')); // ya la tiene
  const tiles = albumTiles(c.specials);
  assert.equal(tiles.length, 15);
  assert.deepEqual(
    tiles.filter((t) => t.owned).map((t) => t.label),
    ['Rubí'],
  );
});

test('valor de mercado y goles por partido', () => {
  assert.equal(coinsText(480), '480 monedas');
  assert.equal(coinsText(1480), '1.480 monedas');
  assert.equal(goalsPerMatch(player()), '0,75');
  assert.equal(goalsPerMatch(player({ matches: 0, goals: 0 })), '0');
});
