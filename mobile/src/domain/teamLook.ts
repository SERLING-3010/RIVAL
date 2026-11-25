// Escudo y diseño del equipo (Sprint 23). El escudo se arma con piezas de RIVAL: no se suben imágenes.
// Se guarda como "FORMA|#color1|#color2|SÍMBOLO"; sin escudo guardado se usa el predeterminado.

export const CREST_SHAPES = ['ESCUDO', 'CIRCULO', 'ROMBO', 'BANDERA'] as const;
export const CREST_SYMBOLS = ['INICIALES', 'ESTRELLA', 'RAYO', 'CORONA', 'BALON'] as const;
export const CREST_COLORS = [
  '#0B6B3A',
  '#2BD46B',
  '#06120C',
  '#FFFFFF',
  '#F6DE92',
  '#C0182F',
  '#FF7A33',
  '#1D4ED8',
  '#0EA5E9',
  '#7B4BB0',
] as const;

export type CrestShape = (typeof CREST_SHAPES)[number];
export type CrestSymbol = (typeof CREST_SYMBOLS)[number];

export interface Crest {
  shape: CrestShape;
  primary: string;
  secondary: string;
  symbol: CrestSymbol;
}

export const SHAPE_LABEL: Record<CrestShape, string> = {
  ESCUDO: 'Escudo',
  CIRCULO: 'Círculo',
  ROMBO: 'Rombo',
  BANDERA: 'Bandera',
};

export const SYMBOL_LABEL: Record<CrestSymbol, string> = {
  INICIALES: 'Iniciales',
  ESTRELLA: 'Estrella',
  RAYO: 'Rayo',
  CORONA: 'Corona',
  BALON: 'Balón',
};

/** El de siempre: cuadro verde con las iniciales en blanco. */
export const DEFAULT_CREST: Crest = {
  shape: 'ESCUDO',
  primary: '#0B6B3A',
  secondary: '#FFFFFF',
  symbol: 'INICIALES',
};

const isShape = (v: string): v is CrestShape => (CREST_SHAPES as readonly string[]).includes(v);
const isSymbol = (v: string): v is CrestSymbol => (CREST_SYMBOLS as readonly string[]).includes(v);

/** null = sin escudo guardado (o uno que ya no es válido): se muestra el predeterminado. */
export function parseCrest(raw: string | null): Crest | null {
  if (!raw) return null;
  const [shape = '', primary = '', secondary = '', symbol = ''] = raw.split('|');
  if (!isShape(shape) || !isSymbol(symbol)) return null;
  return { shape, primary, secondary, symbol };
}

export function encodeCrest(c: Crest): string {
  return [c.shape, c.primary, c.secondary, c.symbol].join('|');
}

/** El diseño elegible: "BASIC" es la carta básica de hoy; el resto, especiales ganadas. */
export const BASIC = 'BASIC';
