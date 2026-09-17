// Third Party
import type { TFunction } from 'i18next';
import { describe, expect, it, vi } from 'vitest';

// AA Belt Radar
import {
    getBeltTimerColumns,
    getSessionColumns,
    getSnapshotColumns,
} from '@/Components/Tables/TableColumns';

describe('TableColumns definitions', () => {
    const mockT = ((key: string) => `trans_${key}`) as unknown as TFunction;
    const mockOnSelect = vi.fn();
    const mockSetModalAction = vi.fn();

    describe('getSessionColumns', () => {
        it('returns 6 column definitions with correct headers', () => {
            const columns = getSessionColumns(mockT, mockOnSelect, mockSetModalAction);
            expect(columns).toHaveLength(6);

            const headers = columns.map((col) =>
                typeof col.header === 'string' ? col.header : undefined,
            );
            expect(headers).toEqual([
                'trans_Public ID',
                'trans_Name',
                'trans_Created At',
                'trans_Owner',
                'trans_Public',
                'trans_Actions',
            ]);
        });

        it('has correct accessors for session fields', () => {
            const columns = getSessionColumns(mockT, mockOnSelect, mockSetModalAction);
            const accessors = columns.map((col) => (col as { accessorKey?: string }).accessorKey);
            expect(accessors).toContain('public_id');
            expect(accessors).toContain('name');
            expect(accessors).toContain('created_at');
            expect(accessors).toContain('owner.portrait');
            expect(accessors).toContain('public.display');
            expect(accessors).toContain('actions');
        });
    });

    describe('getBeltTimerColumns', () => {
        it('returns 7 column definitions with correct headers', () => {
            const columns = getBeltTimerColumns(mockT, mockOnSelect, mockSetModalAction);
            expect(columns).toHaveLength(7);

            const headers = columns.map((col) =>
                typeof col.header === 'string' ? col.header : undefined,
            );
            expect(headers).toEqual([
                'trans_Public ID',
                'trans_Belt Name',
                'trans_Belt Size',
                'trans_Belt Type',
                'trans_ETA',
                'trans_Public',
                'trans_Actions',
            ]);
        });

        it('has correct accessors for belt timer fields', () => {
            const columns = getBeltTimerColumns(mockT, mockOnSelect, mockSetModalAction);
            const accessors = columns.map((col) => (col as { accessorKey?: string }).accessorKey);
            expect(accessors).toContain('public_id');
            expect(accessors).toContain('belt_name');
            expect(accessors).toContain('belt_size');
            expect(accessors).toContain('belt_type');
            expect(accessors).toContain('eta.display');
            expect(accessors).toContain('public.display');
            expect(accessors).toContain('actions');
        });
    });

    describe('getSnapshotColumns', () => {
        it('returns 6 column definitions for snapshot ore list', () => {
            const columns = getSnapshotColumns(mockT);
            expect(columns).toHaveLength(6);

            const headers = columns.map((col) =>
                typeof col.header === 'string' ? col.header : undefined,
            );
            expect(headers).toEqual([
                'trans_Ore',
                'trans_Units Left',
                'trans_Volume Left (m³)',
                'trans_Price (ISK/m³)',
                'trans_Price Compressed',
                'trans_Income Compressed (ISK/h)',
            ]);
        });

        it('has cell formatter for numeric fields', () => {
            const columns = getSnapshotColumns(mockT);
            const unitsCol = columns.find((col) => (col as { accessorKey?: string }).accessorKey === 'units');
            expect(unitsCol).toBeDefined();
            expect(typeof unitsCol?.cell).toBe('function');
        });
    });
});
