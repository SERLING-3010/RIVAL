// Pruebas de logros e insignias. Ejecutar: node --experimental-strip-types --test tests/
import assert from 'node:assert/strict';
import { test } from 'node:test';

import type { Badge } from '../src/domain/badgeModels.ts';
import { splitBadges } from '../src/domain/badgeModels.ts';

const b = (code: string, earned: string | null): Badge => ({
  code,
  name: code,
  description: '',
  earned_at: earned,
  progress: earned ? null : '0/1',
});

test('splitBadges: ganadas de la más reciente a la más antigua y pendientes en su orden', () => {
  const { earned, pending } = splitBadges([
    b('DEBUT', '2026-11-01T10:00:00Z'),
    b('MATCHES_10', null),
    b('HAT_TRICK', '2026-11-20T10:00:00Z'),
    b('GOALS_10', null),
  ]);
  assert.deepEqual(
    earned.map((x) => x.code),
    ['HAT_TRICK', 'DEBUT'],
  );
  assert.deepEqual(
    pending.map((x) => x.code),
    ['MATCHES_10', 'GOALS_10'],
  );
});
