// Carta nueva por revelar (Sprint 23): compara lo ganado con lo ya mostrado en este teléfono.

import { useCallback, useEffect, useRef, useState } from 'react';

import type { SpecialCard, SpecialTier } from '../domain/cardModels';
import { earnedSignature, markSeen, toReveal } from '../domain/newCards';
import { readSeen, saveSeen } from '../services/seenCardsStore';

export interface NewCardController {
  reveal: SpecialTier | null;
  handleDone: () => void;
}

/** key null = no aplica (por ejemplo, la ficha de otro jugador). */
export function useNewCard(key: string | null, specials: SpecialCard[] | null): NewCardController {
  const [reveal, setReveal] = useState<SpecialTier | null>(null);
  const seen = useRef<string[]>([]);
  const current = useRef<SpecialCard[]>([]);
  current.current = specials ?? [];
  const signature = earnedSignature(specials);
  useEffect(() => {
    if (key === null || signature === '') return undefined;
    let alive = true;
    void readSeen(key).then((stored) => {
      if (!alive) return;
      seen.current = stored;
      setReveal(toReveal(current.current, stored));
    });
    return () => {
      alive = false;
    };
  }, [key, signature]);
  const handleDone = useCallback(() => {
    setReveal(null);
    if (key === null) return;
    seen.current = markSeen(current.current, seen.current);
    void saveSeen(key, seen.current);
  }, [key]);
  return { reveal, handleDone };
}
