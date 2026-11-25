// Plantilla en modo juego: carga el equipo y, para comparar, las fichas de dos jugadores.

import { useCallback, useState } from 'react';

import type { PlayerCard } from '../domain/managerModels';
import type { Squad } from '../domain/squadModels';
import { managerApi } from '../services/managerApi';
import { squadApi } from '../services/squadApi';
import type { Action } from './useAction';
import { useAction } from './useAction';
import type { Loader } from './useLoader';
import { useLoader } from './useLoader';

export interface SquadController extends Loader<Squad> {
  compare: Loader<[PlayerCard, PlayerCard]> | null;
  picked: number[];
  handlePick: (userId: number) => void;
  action: Action; // Sprint 23: escudo y diseño
  handleChooseDesign: (choice: string | null) => Promise<void>;
  handleSaveCrest: (crest: string | null) => Promise<void>;
}

export function useSquad(token: string, teamId: number): SquadController {
  const loader = useLoader(
    () => squadApi.get(token, teamId),
    () => false,
    '',
    `squad|${teamId}`,
  );
  const [picked, setPicked] = useState<number[]>([]);
  const [first, second] = picked;
  const compare = useLoader<[PlayerCard, PlayerCard]>(
    () =>
      first === undefined || second === undefined
        ? Promise.reject(new Error('elige dos jugadores'))
        : Promise.all([managerApi.card(token, first), managerApi.card(token, second)]),
    () => false,
    '',
    `compare|${first ?? '-'}|${second ?? '-'}`,
  );
  /** Toca un jugador para elegirlo; con dos elegidos, el siguiente reemplaza al más antiguo. */
  const handlePick = useCallback((userId: number) => {
    setPicked((p) => (p.includes(userId) ? p.filter((x) => x !== userId) : [...p, userId].slice(-2)));
  }, []);
  const action = useAction();
  const { handleReload } = loader;
  const handleChooseDesign = useCallback(
    (choice: string | null) =>
      action.run(
        () => squadApi.chooseDesign(token, teamId, choice),
        'Diseño del equipo cambiado.',
        handleReload,
      ),
    [action, handleReload, teamId, token],
  );
  const handleSaveCrest = useCallback(
    (crest: string | null) =>
      action.run(() => squadApi.setCrest(token, teamId, crest), 'Escudo guardado.', handleReload),
    [action, handleReload, teamId, token],
  );
  return {
    ...loader,
    compare: picked.length === 2 ? compare : null,
    picked,
    handlePick,
    action,
    handleChooseDesign,
    handleSaveCrest,
  };
}
