# React Development Guidelines

When working on frontend code in this repository, strictly adhere to the following rules:

## 1. Always Use `@/` Import Paths (Never Relative `./` or `../`)

- All internal project imports and exports must **always** use the `@/` path alias (which resolves to `frontend/src/`).
- Do **not** use relative imports such as `./` or `../`.

### Examples:

```typescript
// ❌ INCORRECT (relative paths)
import { SnapshotSelect } from './SnapshotSelect';
import { formatDate } from '../../Helpers/functions';
import BaseTable from '../BaseTable';
export { default as SnapshotButtons } from './SnapshotButtons';

// ✅ CORRECT (always use @/)
import { SnapshotSelect } from '@/Components/Tables/Snapshot/SnapshotSelect';
import { formatDate } from '@/Components/Helpers/functions';
import BaseTable from '@/Components/Tables/BaseTable';
export { default as SnapshotButtons } from '@/Components/Tables/Snapshot/SnapshotButtons';
```

## 2. Topic-Based Component Folders (under `Tables/`, etc.)

- Organize related subcomponents into dedicated topic folders (e.g. `Components/Tables/Snapshot/`).
- Keep components small, modular, and focused (e.g., `<SnapshotSelect />`, `<SnapshotButtons />`).
- Each folder should contain an `index.ts` file that re-exports components using `@/` path aliases.

### Example Structure:

```text
frontend/src/Components/Tables/
├── Snapshot/
│   ├── SnapshotSelect.tsx    # Dropdown selector component
│   ├── SnapshotButtons.tsx   # Action buttons component (Add/Delete)
│   └── index.ts              # Exports using @/ aliases
├── BaseTable.tsx
└── ...
```

## 3. Import Grouping & Ordering

Follow the project import order convention:

1. **React**:
   ```typescript
   import { useState, useMemo } from 'react';
   import { useParams } from 'react-router-dom';
   ```
1. **Third-Party Libraries**:
   ```typescript
   import { useQuery } from '@tanstack/react-query';
   import Form from 'react-bootstrap/Form';
   import { useTranslation } from 'react-i18next';
   ```
1. **AA Belt Radar (`@/`)**:
   ```typescript
   import { loadSnapshot } from '@/Api/BeltRadar';
   import { queryKeys } from '@/Api/query';
   import { formatDate } from '@/Components/Helpers/functions';
   import { SnapshotButtons, SnapshotSelect } from '@/Components/Tables/Snapshot';
   ```
1. **Styles & CSS**:
   ```typescript
   import styles from '@/Components/Tables/BaseTable.module.css';
   ```

## 4. TypeScript & Prop Interfaces

- Export explicit TypeScript prop interfaces for components (`export interface ...Props`).
- Provide sensible defaults for optional arrays or identifiers (`snapshots = []`, etc.).
