// Third Party
import { describe, expect, it } from 'vitest';

// AA Belt Radar
import {
    getBeltSizeValue,
    getBeltTypeValue,
    hasRequiredFields,
    validateAddSnapshotForm,
    validateBeltTimerForm,
    validateSessionForm,
} from '@/Components/Forms/validation';

describe('validation functions', () => {
    describe('hasRequiredFields', () => {
        const validator = hasRequiredFields('foo', 'bar');

        it('returns true when all required fields are present and non-empty', () => {
            expect(validator({ foo: 'val1', bar: 'val2' })).toBe(true);
        });

        it('returns false when a required field is missing', () => {
            expect(validator({ foo: 'val1' })).toBe(false);
        });

        it('returns false when a required field is an empty string or only whitespace', () => {
            expect(validator({ foo: 'val1', bar: '   ' })).toBe(false);
            expect(validator({ foo: '', bar: 'val2' })).toBe(false);
        });

        it('returns false when a required field is not a string', () => {
            expect(validator({ foo: 123, bar: 'val2' } as unknown as Record<string, unknown>)).toBe(false);
        });
    });

    describe('validateSessionForm', () => {
        it('validates session form requires non-empty name', () => {
            expect(validateSessionForm({ name: 'Mining Ops' })).toBe(true);
            expect(validateSessionForm({ name: '  ' })).toBe(false);
            expect(validateSessionForm({})).toBe(false);
        });
    });

    describe('validateAddSnapshotForm', () => {
        it('validates snapshot form requires non-empty raw_data', () => {
            expect(validateAddSnapshotForm({ raw_data: 'Veldspar 1000' })).toBe(true);
            expect(validateAddSnapshotForm({ raw_data: '' })).toBe(false);
            expect(validateAddSnapshotForm({})).toBe(false);
        });
    });

    describe('validateBeltTimerForm', () => {
        it('returns true for complete valid belt timer data with belt_id <= 7 chars', () => {
            const validData = {
                belt_id: 'BELT-1',
                belt_name: 'Belt 1',
                belt_type: 'asteroid_belt',
                belt_size: 'medium',
            };
            expect(validateBeltTimerForm(validData)).toBe(true);
        });

        it('returns false if belt_id exceeds 7 characters', () => {
            const longIdData = {
                belt_id: 'TOOLONG123',
                belt_name: 'Belt 1',
                belt_type: 'asteroid_belt',
                belt_size: 'medium',
            };
            expect(validateBeltTimerForm(longIdData)).toBe(false);
        });

        it('returns false if any required field is missing', () => {
            expect(validateBeltTimerForm({
                belt_name: 'Belt 1',
                belt_type: 'asteroid_belt',
                belt_size: 'medium',
            })).toBe(false);

            expect(validateBeltTimerForm({
                belt_id: 'B1',
                belt_name: '',
                belt_type: 'asteroid_belt',
                belt_size: 'medium',
            })).toBe(false);
        });
    });

    describe('getBeltTypeValue', () => {
        it('resolves value from matching option value', () => {
            expect(getBeltTypeValue('asteroid_belt')).toBe('asteroid_belt');
            expect(getBeltTypeValue('ice_belt')).toBe('ice_belt');
        });

        it('resolves value from matching option label case-insensitively', () => {
            expect(getBeltTypeValue('Asteroid Belt')).toBe('asteroid_belt');
            expect(getBeltTypeValue('ice belt')).toBe('ice_belt');
            expect(getBeltTypeValue('Mercoxit Belt')).toBe('mercoxit');
        });

        it('returns original string if unknown', () => {
            expect(getBeltTypeValue('custom_belt')).toBe('custom_belt');
        });

        it('returns empty string if falsy', () => {
            expect(getBeltTypeValue(undefined)).toBe('');
            expect(getBeltTypeValue('')).toBe('');
        });
    });

    describe('getBeltSizeValue', () => {
        it('resolves value from matching size value or label', () => {
            expect(getBeltSizeValue('small')).toBe('small');
            expect(getBeltSizeValue('Medium')).toBe('medium');
            expect(getBeltSizeValue('COLOSSAL')).toBe('colossal');
            expect(getBeltSizeValue('ice')).toBe('ice');
        });

        it('returns original string if unknown', () => {
            expect(getBeltSizeValue('extra_huge')).toBe('extra_huge');
        });

        it('returns empty string if falsy', () => {
            expect(getBeltSizeValue(undefined)).toBe('');
            expect(getBeltSizeValue('')).toBe('');
        });
    });
});
