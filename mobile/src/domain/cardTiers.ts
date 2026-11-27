// Cartas (Sprint 23): cuatro básicas por media y quince especiales por media + hazañas. El backend
// decide cuál tiene cada jugador; aquí solo vive cómo se ve cada una. Nada se compra.

export const BASE_CODES = ['BRONCE', 'PLATA', 'ORO', 'ORO_BRILLANTE'] as const;
export const SPECIAL_CODES = [
  'RUBI',
  'ESMERALDA',
  'DIAMANTE',
  'PADPARADSCHA',
  'ALEJANDRITA',
  'FANTASIA',
  'GRANDIDIERITA',
  'SERENDIBITA',
  'PAINITA',
  'TAAFFEITA',
  'DIAMANTE_ROJO',
  'CORONA',
  'PRISMA',
  'GALAXIA',
  'ELITE',
] as const;
export const TIER_CODES = [...BASE_CODES, ...SPECIAL_CODES] as const;

export type BaseTier = (typeof BASE_CODES)[number];
export type SpecialTier = (typeof SPECIAL_CODES)[number];
export type CardTier = BaseTier | SpecialTier;
export type Rarity = 'BÁSICA' | 'RARA' | 'ÉPICA' | 'MÍTICA' | 'LEGENDARIA' | 'SUPREMA' | 'ÚNICA';
export type Foil = [string, string, string, string, string];

export interface TierLook {
  label: string;
  rarity: Rarity;
  media: number; // media desde la que se tiene (básicas) o mínima (especiales)
  foil: Foil; // paradas del degradado (claro, oscuro, brillo, oscuro, claro)
  ink: string; // color del texto sobre la lámina
  swatch: string; // color de la casilla del álbum
  sheen: boolean; // brillo que recorre la lámina
  stars: string | null; // destellos que titilan
  glow: string | null; // borde interior que late
  shift: Foil | null; // segunda lámina que aparece y desaparece (Alejandrita)
  holo: boolean; // franja tornasol que corre
  aurora: boolean; // aurora que va y viene (Élite)
  frame: string | null; // marco de color propio
  emblem: 'crown' | 'neon' | null;
}

type Fx = Partial<Omit<TierLook, 'label' | 'rarity' | 'media' | 'ink' | 'swatch' | 'foil'>>;
const NONE = { sheen: true, stars: null, glow: null, shift: null, holo: false, aurora: false, frame: null };

function t(h: [string, Rarity, number, string, string], foil: string, fx: Fx = {}): TierLook {
  const [label, rarity, media, ink, swatch] = h;
  return { label, rarity, media, ink, swatch, foil: foil.split(' ') as Foil, ...NONE, emblem: null, ...fx };
}

const D = '#1A1206';
const W = '#FFFFFF';
const GOLD = '#FFF3C4 #C99A35 #FBE7A1 #A87A22 #F1D27A';

// Una fila por carta: [nombre, rareza, media, tinta, casilla], degradado y efectos.
// prettier-ignore
export const TIERS: Record<CardTier, TierLook> = {
  BRONCE: t(['Bronce', 'BÁSICA', 0, D, '#B07945'], '#F3CFA9 #B07945 #F0C493 #8A5A35 #D9A374', { sheen: false }),
  PLATA: t(['Plata', 'BÁSICA', 65, '#1E2328', '#C9D3D9'], '#FFFFFF #A9B3BA #F2F5F7 #8C979E #DDE3E7'),
  ORO: t(['Oro común', 'BÁSICA', 75, D, '#E6C25C'], GOLD),
  ORO_BRILLANTE: t(['Oro brillante', 'ÚNICA', 80, D, '#FFE27A'], GOLD, { frame: '#FFF8E0', holo: true, stars: W }),
  RUBI: t(['Rubí', 'RARA', 75, W, '#D0213C'], '#FF6B7A #C0182F #FF8A96 #6E0B1B #B0142B'),
  ESMERALDA: t(['Esmeralda', 'RARA', 75, W, '#13A86A'], '#46E0A0 #0E8F5A #6FF0B8 #05402A #0B7A4C'),
  DIAMANTE: t(['Diamante', 'ÉPICA', 78, '#0B2230', '#9FE3FF'], '#E8FAFF #8FD8F5 #FFFFFF #5BB8E0 #DDF6FF',
    { stars: W }),
  PADPARADSCHA: t(['Zafiro Padparadscha', 'ÉPICA', 78, D, '#FF8A8A'], '#FFD3B6 #FF9A8B #FFE3D3 #FF6A88 #E0507A'),
  ALEJANDRITA: t(['Alejandrita', 'ÉPICA', 80, W, '#7B4BB0'], '#3FD19A #0F7A55 #5FE3B0 #064A33 #0B6545',
    { shift: ['#E07AC8', '#8E2C8A', '#F09ADB', '#4A0E4E', '#6E1E6E'] }),
  FANTASIA: t(['Diamante Fantasía', 'MÍTICA', 80, D, '#B7C8FF'], '#8EC5FF #C8E2FF #FFFFFF #FFC8E6 #FF8EC8',
    { stars: W, holo: true }),
  GRANDIDIERITA: t(['Grandidierita', 'MÍTICA', 82, '#06302E', '#4FC6BA'], '#BEFFF8 #5FD3C7 #E6FFFC #2C9C9A #7FE6DB',
    { glow: 'rgba(255,255,255,0.9)' }),
  SERENDIBITA: t(['Serendibita', 'MÍTICA', 82, '#E6F4F7', '#123446'], '#1D4F5A #0B2433 #2E6A78 #050C14 #0F3040',
    { stars: '#BFEFFF' }),
  PAINITA: t(['Painita', 'LEGENDARIA', 84, '#FFF4EC', '#C0582E'], '#F2A15E #B4492B #FFC08A #5E1E10 #8E3420',
    { glow: 'rgba(255,150,80,0.95)' }),
  TAAFFEITA: t(['Taaffeíta', 'LEGENDARIA', 85, W, '#A07AC0'], '#E3C6F2 #B58AC6 #F2E2FA #7A4C9E #4A2A68',
    { holo: true, glow: 'rgba(230,200,255,0.95)' }),
  DIAMANTE_ROJO: t(['Diamante Rojo', 'LEGENDARIA', 86, W, '#E0193B'], '#FF5C77 #9E0022 #FF7A90 #5A0012 #B3002A',
    { stars: '#FFE0E6', glow: 'rgba(255,40,80,1)' }),
  CORONA: t(['Corona', 'SUPREMA', 87, '#F6DE92', '#C99A35'], '#1A1A1A #050505 #262626 #050505 #121212',
    { frame: '#D9B24E', emblem: 'crown' }),
  PRISMA: t(['Prisma', 'SUPREMA', 88, '#06120C', '#C77DFF'], '#2BD46B #7AE0FF #C77DFF #FF8EC8 #FFE27A',
    { frame: '#EAF5EE', holo: true, stars: W }),
  GALAXIA: t(['Galaxia', 'SUPREMA', 90, '#EAF5EE', '#1E2A6E'], '#0B2A3A #03060F #1C2A6E #03060F #0E3B2A',
    { frame: '#7AE0FF', stars: W, glow: 'rgba(122,124,255,0.9)' }),
  ELITE: t(['Élite', 'ÚNICA', 92, '#B9F5CF', '#2BD46B'], '#0E2A1C #030605 #0E2A1C #030605 #06120C',
    { sheen: false, frame: '#2BD46B', aurora: true, stars: '#F6DE92', glow: 'rgba(43,212,107,1)', emblem: 'neon' }),
};

export const TIER_LABEL = Object.fromEntries(TIER_CODES.map((c) => [c, TIERS[c].label])) as Record<
  CardTier,
  string
>;
