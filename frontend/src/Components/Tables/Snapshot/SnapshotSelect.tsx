// Third Party
import Form from 'react-bootstrap/Form';
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import type { components } from '@/Api/OpenApi';
import { formatDate } from '@/Components/Tables/BaseTable/tableHelper';

export interface SnapshotSelectProps {
  snapshots?: components['schemas']['SnapshotSummarySchema'][];
  selectedSnapshotId?: string | null;
  fallbackIdentifier?: string | null;
  onSelect: (identifier: string | null) => void;
}

export function SnapshotSelect({
  snapshots = [],
  selectedSnapshotId,
  fallbackIdentifier = '',
  onSelect,
}: SnapshotSelectProps) {
  const { t } = useTranslation();

  if (!snapshots || snapshots.length === 0) {
    return null;
  }

  const currentIdentifier = selectedSnapshotId ?? fallbackIdentifier ?? '';

  return (
    <Form.Select
      size="sm"
      className="w-auto"
      value={currentIdentifier}
      onChange={(e) => {
        const val = e.target.value;
        onSelect(val === snapshots[0]?.identifier ? null : val);
      }}
      disabled={snapshots.length <= 1}
      aria-label={t('Select Snapshot')}
    >
      {snapshots.map((s, index) => {
        const isLatest = index === 0;
        const dateStr = formatDate(s.timestamp, {
          dateStyle: 'short',
          timeStyle: 'medium',
        });
        const countStr =
          s.asteroid_count != null ? ` (${s.asteroid_count} ${t('asteroids')})` : '';
        const label = isLatest
          ? `${dateStr} (${t('Latest')})${countStr}`
          : `${dateStr}${countStr}`;
        return (
          <option key={s.identifier} value={s.identifier}>
            {label}
          </option>
        );
      })}
    </Form.Select>
  );
}

export default SnapshotSelect;
