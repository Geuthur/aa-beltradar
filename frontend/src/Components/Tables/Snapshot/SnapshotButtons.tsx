// Third Party
import { ButtonGroup } from 'react-bootstrap';

// AA Belt Radar
import type { components } from '@/Api/OpenApi';
import { ActionButton } from '@/Components/Icons/Icons';

export interface SnapshotButtonsProps {
  addAction?: components['schemas']['ModalSchema'] | null;
  deleteAction?: components['schemas']['ModalSchema'] | null;
  onAddClick: () => void;
  onDeleteClick: () => void;
}

export function SnapshotButtons({
  addAction,
  deleteAction,
  onAddClick,
  onDeleteClick,
}: SnapshotButtonsProps) {
  if (!addAction && !deleteAction) {
    return null;
  }

  return (
    <ButtonGroup size="sm">
      {addAction && <ActionButton action={addAction} onClick={onAddClick} />}
      {deleteAction && <ActionButton action={deleteAction} onClick={onDeleteClick} />}
    </ButtonGroup>
  );
}

export default SnapshotButtons;
