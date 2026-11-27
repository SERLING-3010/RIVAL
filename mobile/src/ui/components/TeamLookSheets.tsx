// Las dos ventanas de la imagen del equipo (Sprint 23): armar el escudo y elegir el diseño de la media.

import type { SquadController } from '../../controllers/useSquad';
import type { Squad } from '../../domain/squadModels';
import { parseCrest } from '../../domain/teamLook';
import { CrestEditor } from './CrestEditor';
import { DesignPicker } from './DesignPicker';

interface Props {
  squad: Squad;
  sheet: 'crest' | 'design' | null;
  controller: SquadController;
  onClose: () => void;
}

export function TeamLookSheets({ squad, sheet, controller, onClose }: Props) {
  if (!squad.can_edit) return null;
  return (
    <>
      <CrestEditor
        visible={sheet === 'crest'}
        initial={parseCrest(squad.crest)}
        teamName={squad.team.name}
        busy={controller.action.busy}
        onSave={(crest) => {
          onClose();
          void controller.handleSaveCrest(crest);
        }}
        onClose={onClose}
      />
      {squad.card ? (
        <DesignPicker
          visible={sheet === 'design'}
          basic={squad.card.tier}
          available={squad.card.available}
          chosen={squad.card.chosen}
          onPick={(choice) => {
            onClose();
            void controller.handleChooseDesign(choice);
          }}
          onClose={onClose}
        />
      ) : null}
    </>
  );
}
