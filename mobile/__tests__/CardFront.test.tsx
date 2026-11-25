import { describe, expect, test } from '@jest/globals';
import { render, screen } from '@testing-library/react-native';

import { TIER_CODES, TIERS } from '../src/domain/cardTiers';
import { CardFront } from '../src/ui/components/CardFront';

const face = (tier: (typeof TIER_CODES)[number]) => ({
  media: 81,
  position: 'DEL',
  crest: 'CH',
  tier,
  name: 'Andrés Mejía',
  stats: [{ value: '24', label: 'PJ' }],
});

describe('CardFront', () => {
  test.each(TIER_CODES)('dibuja la carta %s con su nombre de nivel', async (tier) => {
    await render(<CardFront face={face(tier)} />);
    expect(screen.getByText(TIERS[tier].label.toUpperCase())).toBeTruthy();
    expect(screen.getByText('81')).toBeTruthy();
  });

  test('Corona y Élite llevan emblema en lugar de silueta', async () => {
    await render(<CardFront face={face('ELITE')} />);
    expect(screen.getByLabelText('Símbolo de RIVAL en neón')).toBeTruthy();
    expect(screen.queryByLabelText('Sin foto: silueta del jugador')).toBeNull();
    await render(<CardFront face={face('CORONA')} />);
    expect(screen.getByLabelText('Corona')).toBeTruthy();
  });
});
