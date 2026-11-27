import { describe, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';

import type { TacticsController } from '../src/controllers/useTactics';
import type { Tactic, TacticDraft } from '../src/domain/tacticsModels';
import { TacticsScreen } from '../src/ui/screens/TacticsScreen';
import { idleAction } from './fixtures';

const tactic = (over: Partial<Tactic> = {}): Tactic => ({
  contract_id: 7,
  team_id: 1,
  players_per_side: 1,
  uses_formation: false,
  suggested_formations: [],
  formation: null,
  starters: [],
  subs: [],
  eligible: [
    { user_id: 1, display_name: 'Ana', position: null, still_going: true },
    { user_id: 2, display_name: 'Luis', position: null, still_going: true },
  ],
  can_edit: true,
  ...over,
});

const controller = (t: Tactic): TacticsController => ({
  state: { kind: 'success', data: t },
  handleReload: jest.fn(),
  action: idleAction(),
  handleSave: jest.fn(async (_d: TacticDraft, _t: Tactic) => null),
});

describe('TacticsScreen', () => {
  test('el administrador elige titular con posición y guarda', async () => {
    const c = controller(tactic());
    await render(<TacticsScreen controller={c} onBack={jest.fn()} />);
    await fireEvent.press(screen.getAllByText('Titular')[0]!);
    await fireEvent.changeText(screen.getByLabelText('Posición de Ana'), 'Base');
    await fireEvent.press(screen.getByText('Guardar alineación'));
    const [draft] = (c.handleSave as jest.Mock).mock.calls[0] as [TacticDraft, Tactic];
    expect(draft.roles[1]).toBe('starter');
    expect(draft.positions[1]).toBe('Base');
  });

  test('un jugador ve la alineación sin editar y se marca quien ya no va', async () => {
    const t = tactic({
      can_edit: false,
      starters: [{ user_id: 1, display_name: 'Ana', position: 'Base', still_going: false }],
      eligible: [],
    });
    await render(<TacticsScreen controller={controller(t)} onBack={jest.fn()} />);
    expect(screen.getByText('Ana (ya no va) · Base')).toBeTruthy();
    expect(screen.queryByText('Guardar alineación')).toBeNull();
  });
});
