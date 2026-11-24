// Tokens de diseño: escala Slate, un solo color de acento y colores de estado con significado.

export const colors = {
  background: '#F8FAFC',
  surface: '#FFFFFF',
  border: '#E2E8F0',
  text: '#0F172A',
  textMuted: '#475569',
  accent: '#1D4ED8',
  accentText: '#FFFFFF',
  success: '#15803D',
  warning: '#B45309',
  danger: '#B91C1C',
  disabled: '#94A3B8',
} as const;

export const space = { xs: 4, sm: 8, md: 16, lg: 24, xl: 32 } as const;

export const radius = { sm: 8, md: 12 } as const;

export const font = {
  title: 24,
  heading: 18,
  body: 16,
  small: 14,
} as const;

// Objetivo táctil mínimo recomendado para accesibilidad.
export const MIN_TOUCH = 44;
