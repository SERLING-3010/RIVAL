// Sprint 29: carga una vez el alcance del lanzamiento. Si falla, se queda con todo prendido: el
// backend sigue rechazando lo apagado, así que nunca se habilita algo que no esté disponible.

import { useEffect, useState } from 'react';

import type { Features } from '../domain/features';
import { ALL_FEATURES } from '../domain/features';
import { featuresApi } from '../services/featuresApi';

export function useLaunchFeatures(): Features {
  const [features, setFeatures] = useState<Features>(ALL_FEATURES);
  useEffect(() => {
    let alive = true;
    void featuresApi
      .get()
      .then((f) => {
        if (alive) setFeatures(f);
      })
      .catch(() => undefined);
    return () => {
      alive = false;
    };
  }, []);
  return features;
}
