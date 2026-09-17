/**
 * Helper functions for form validation and select choices
 */

export interface SelectOption {
    value: string;
    label: string;
}

export const BELT_TYPE_OPTIONS: SelectOption[] = [
    { value: 'asteroid_belt', label: 'Asteroid Belt' },
    { value: 'ice_belt', label: 'Ice Belt' },
    { value: 'mercoxit', label: 'Mercoxit Belt' },
    { value: 'array_belt', label: 'Array Belt' },
];

export const BELT_SIZE_CHOICES_BY_TYPE: Record<string, SelectOption[]> = {
    asteroid_belt: [
        { value: 'small', label: 'Small' },
        { value: 'medium', label: 'Medium' },
        { value: 'large', label: 'Large' },
        { value: 'enormous', label: 'Enormous' },
        { value: 'colossal', label: 'Colossal' },
    ],
    array_belt: [
        { value: 'small', label: 'Small' },
        { value: 'medium', label: 'Medium' },
        { value: 'large', label: 'Large' },
    ],
    mercoxit: [
        { value: 'small', label: 'Small' },
        { value: 'medium', label: 'Medium' },
        { value: 'large', label: 'Large' },
        { value: 'enormous', label: 'Enormous' },
    ],
    ice_belt: [
        { value: 'ice', label: 'Ice' },
    ],
};

export const ALL_BELT_SIZES: SelectOption[] = [
    { value: 'small', label: 'Small' },
    { value: 'medium', label: 'Medium' },
    { value: 'large', label: 'Large' },
    { value: 'enormous', label: 'Enormous' },
    { value: 'colossal', label: 'Colossal' },
    { value: 'ice', label: 'Ice' },
];

/**
 * Checks if the specified fields are present and non-empty in the given data object.
 */
export const hasRequiredFields = (...fields: string[]) =>
    (data: Record<string, unknown>) =>
        fields.every((field) => typeof data[field] === 'string' && data[field].trim().length > 0);

export const validateSessionForm = hasRequiredFields('name');

export const validateBeltTimerForm = (data: Record<string, unknown>): boolean => {
    const hasRequired = hasRequiredFields('belt_id', 'belt_name', 'belt_type', 'belt_size')(data);
    if (!hasRequired) return false;
    const beltId = String(data.belt_id ?? '').trim();
    return beltId.length <= 7;
};

/**
 * Resolves a belt type value from either a choice value or a display label.
 */
export const getBeltTypeValue = (labelOrValue?: string): string => {
    if (!labelOrValue) return '';
    const match = BELT_TYPE_OPTIONS.find(
        (opt) =>
            opt.value === labelOrValue ||
            opt.label.toLowerCase() === labelOrValue.toLowerCase(),
    );
    return match ? match.value : labelOrValue;
};

/**
 * Resolves a belt size value from either a choice value or a display label.
 */
export const getBeltSizeValue = (labelOrValue?: string): string => {
    if (!labelOrValue) return '';
    const match = ALL_BELT_SIZES.find(
        (opt) =>
            opt.value === labelOrValue ||
            opt.label.toLowerCase() === labelOrValue.toLowerCase(),
    );
    return match ? match.value : labelOrValue;
};
