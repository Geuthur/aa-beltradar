/* global aaBeltRadarDefaultSettings, aaBeltRadarSettingsOverride, objectDeepMerge, bootstrap */

/**
 * Default settings for aa-beltradar
 * Settings can be overridden by defining aaBeltRadarSettingsOverride before this script is loaded.
 */
const aaBeltRadarSettings = (typeof aaBeltRadarSettingsOverride !== 'undefined')
    ? objectDeepMerge(aaBeltRadarDefaultSettings, aaBeltRadarSettingsOverride) // jshint ignore:line
    : aaBeltRadarDefaultSettings;

/**
 * Bootstrap tooltip by (@ppfeufer)
 *
 * @param {string} [selector=body] Selector for the tooltip elements, defaults to 'body'
 *                                 to apply to all elements with the data-bs-tooltip attribute.
 *                                 Example: 'body', '.my-tooltip-class', '#my-tooltip-id'
 *                                 If you want to apply it to a specific element, use that element's selector.
 *                                 If you want to apply it to all elements with the data-bs-tooltip attribute,
 *                                 use 'body' or leave it empty.
 * @param {string} [namespace=aa-beltradar] Namespace for the tooltip
 * @param {string} [trigger=hover] Trigger for the tooltip ('hover', 'click', etc.)
 * @returns {void}
 */
const _bootstrapTooltip = ({selector = 'body', namespace = 'aa-beltradar', trigger = 'hover'} = {}) => {
    document.querySelectorAll(`${selector} [data-bs-tooltip="${namespace}"]`)
        .forEach((tooltipTriggerEl) => {
            // Dispose existing tooltip instance if it exists
            const existing = bootstrap.Tooltip.getInstance(tooltipTriggerEl);
            if (existing) {
                existing.dispose();
            }

            // Remove any leftover tooltip elements
            $('.bs-tooltip-auto').remove();

            // Create new tooltip instance
            return new bootstrap.Tooltip(tooltipTriggerEl, { trigger });
        });
};

const _bootstrapPopOver = ({selector = 'body', namespace = 'aa-beltradar', trigger = 'hover'} = {}) => {
    document.querySelectorAll(`${selector} [data-bs-popover="${namespace}"]`)
        .forEach((popoverTriggerEl) => {
            // Dispose existing popover instance if it exists
            const existing = bootstrap.Popover.getInstance(popoverTriggerEl);
            if (existing) {
                existing.dispose();
            }

            // Remove any leftover popover elements
            $('.bs-popover-auto').remove();

            // Create new popover instance
            return new bootstrap.Popover(popoverTriggerEl, { trigger });
        });
};




/**
 * Export a DataTables instance to CSV.
 * @param {object} DataTable - The DataTables instance.
 * @param {string} [exportFileName='beltradar.csv'] - The name of the exported CSV file.
 * @throws Will throw an error if the table is not a valid DataTables instance.
 * @returns {void}
 */
const _exportToCSV = (DataTable, exportFileName = 'beltradar.csv') => {
    if (!DataTable || typeof DataTable.columns !== 'function') {
        throw new Error('exportToCSV expects a DataTables instance');
    }

    const escapeCsv = (value) => {
        const str = value == null ? '' : String(value);
        return /[",\n\r]/.test(str) ? `"${str.replace(/"/g, '""')}"` : str;
    };

    const headerCells = DataTable.columns().header().toArray();
    const colCount = DataTable.columns().count();
    const rowIndexes = DataTable.rows({ search: 'applied', page: 'all' }).indexes().toArray();

    const headerRow = Array.from({ length: colCount }, (_, index) => {
        const cell = headerCells[index];
        return cell ? (cell.innerText || cell.textContent || '').trim() : '';
    });

    const rows = rowIndexes.map((rowIndex) => Array.from({ length: colCount }, (_, index) => {
        try {
            return DataTable.cell(rowIndex, index).render('sort');
        } catch (error) {
            console.log(`Error retrieving cell data for row ${rowIndex}, column ${index}:`, error);
            return '';
        }
    }));

    const csv = [headerRow, ...rows]
        .map((line) => line.map(escapeCsv).join(','))
        .join('\n');

    const link = document.createElement('a');
    link.download = exportFileName;
    link.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8;' }));
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
};

/**
* Local POST adapter: keeps global fetchPost untouched while improving error details.
* Reads JSON error payload (message/error/detail) when statusText is empty.
*/
const fetchPostBeltRadar = async ({
    url,
    csrfToken = null,
    payload = null,
    responseIsJson = true
}) => {
    if (!csrfToken) {
        throw new Error('CSRF token is required for POST requests');
    }

    if (payload !== null && (typeof payload !== 'object' || Array.isArray(payload))) {
        throw new Error('Payload must be an object when using POST method');
    }

    const headers = {
        'X-CSRFToken': csrfToken,
    };

    if (responseIsJson) {
        headers.Accept = 'application/json'; // jshint ignore:line
        headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(url, {
        method: 'POST',
        headers,
        body: payload ? JSON.stringify(payload) : null,
    });

    if (!response.ok) {
        let details;
        const contentType = (response.headers.get('content-type') || '').toLowerCase();

        try {
            if (contentType.includes('application/json')) {
                const data = await response.clone().json();
                details = data?.message || data?.error || data?.detail || '';
            } else {
                details = (await response.clone().text()).trim();
            }
        } catch (parseError) {
            details = '';
        }

        const statusText = (response.statusText || '').trim() || 'HTTP Error';
        const msg = details
            ? `Error: ${response.status} - ${statusText} | ${details}`
            : `Error: ${response.status} - ${statusText}`;

        throw new Error(msg);
    }

    return responseIsJson ? await response.json() : await response.text();
};

/**
* Local GET adapter: keeps global fetchGet untouched while improving error details.
* Reads JSON error payload (message/error/detail) when statusText is empty.
*/
const fetchGetBeltRadar = async ({
    url,
    payload = null,
    responseIsJson = true
}) => {
    let requestUrl = url;

    if (payload !== null && (typeof payload !== 'object' || Array.isArray(payload))) {
        throw new Error('Payload must be an object when using GET method');
    }

    if (payload) {
        const queryParams = new URLSearchParams(payload).toString(); // jshint ignore:line
        requestUrl += (url.includes('?') ? '&' : '?') + queryParams;
    }

    const headers = {};
    if (responseIsJson) {
        headers.Accept = 'application/json'; // jshint ignore:line
    }

    const response = await fetch(requestUrl, {
        method: 'GET',
        headers,
    });

    if (!response.ok) {
        let details;
        const contentType = (response.headers.get('content-type') || '').toLowerCase();

        try {
            if (contentType.includes('application/json')) {
                const data = await response.clone().json();
                details = data?.message || data?.error || data?.detail || '';
            } else {
                details = (await response.clone().text()).trim();
            }
        } catch (parseError) {
            details = '';
        }

        const statusText = (response.statusText || '').trim() || 'HTTP Error';
        const msg = details
            ? `Error: ${response.status} - ${statusText} | ${details}`
            : `Error: ${response.status} - ${statusText}`;

        throw new Error(msg);
    }

    return responseIsJson ? await response.json() : await response.text();
};

const sizeChoices = {
    asteroid_belt: [
        ['small', 'Small'],
        ['medium', 'Medium'],
        ['large', 'Large'],
        ['enormous', 'Enormous'],
        ['colossal', 'Colossal'],
    ],
    arrey_belt: [
        ['small', 'Small'],
        ['medium', 'Medium'],
        ['large', 'Large'],
    ],
    mercobelt: [
        ['small', 'Small'],
        ['medium', 'Medium'],
        ['large', 'Large'],
        ['enormous', 'Enormous'],
    ],
    ice_belt: [['ice', 'Ice']],
};

const updateBeltSizeChoices = ({beltTypeSelect, beltSizeSelect}) => {
    const selectedType = beltTypeSelect.value;
    const allowedChoices = sizeChoices[selectedType] || [
        ['small', 'Small'],
        ['medium', 'Medium'],
        ['large', 'Large'],
        ['enormous', 'Enormous'],
        ['colossal', 'Colossal'],
        ['ice', 'Ice'],
    ];
    const previousValue = beltSizeSelect.value;

    beltSizeSelect.innerHTML = '';

    allowedChoices.forEach(([value, label]) => {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = label;
        beltSizeSelect.appendChild(option);
    });

    if (allowedChoices.some(([value]) => value === previousValue)) {
        beltSizeSelect.value = previousValue;
    } else {
        beltSizeSelect.value = allowedChoices[0]?.[0] || '';
    }
};
