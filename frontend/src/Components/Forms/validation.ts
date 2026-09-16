/**
 * Helper functions for form validation
 */

/**
 * Checks if the specified fields are present and non-empty in the given data object.
 */
export const hasRequiredFields = (...fields: string[]) =>
    (data: Record<string, unknown>) =>
        fields.every((field) => typeof data[field] === 'string' && data[field].trim().length > 0);

export const validateSessionForm = hasRequiredFields('name');
