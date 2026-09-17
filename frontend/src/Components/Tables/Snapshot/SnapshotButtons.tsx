// Third Party
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import type { components } from '@/Api/OpenApi';
import { IconButton } from '@/Components/Icons/Icons';

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
  const { t } = useTranslation();

  if (!addAction && !deleteAction) {
    return null;
  }

  return (
    <div className="d-flex gap-2">
      {addAction && (
        <IconButton
          icon={addAction.icon ?? 'fa-solid fa-plus'}
          color={addAction.color ?? 'success'}
          onClick={onAddClick}
          title={addAction.title ?? t('Add Snapshot')}
        />
      )}
      {deleteAction && (
        <IconButton
          icon={deleteAction.icon ?? 'fa-solid fa-trash'}
          color={deleteAction.color ?? 'danger'}
          onClick={onDeleteClick}
          title={deleteAction.title ?? t('Delete Snapshot')}
        />
      )}
    </div>
  );
}

export default SnapshotButtons;
