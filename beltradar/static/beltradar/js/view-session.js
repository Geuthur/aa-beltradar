/* global aaBeltRadarSettings, aaBeltRadarSettingsOverride, _bootstrapTooltip, DataTable, numberFormatter, moment, ApexCharts */

$(document).ready(() => {
    /* DataTable for Belt Radar Session Entries */
    const BeltRadarSessionEntryTable = $('#beltradar-session-entry-table');
    const BeltRadarBeltTimerTable = $('#beltradar-belt-timer-table');
    /* Session details elements */
    const sessionContainer = $('#session-details-container');
    const sessionNameEl = $('#session-name');
    const sessionCreatedAtEl = $('#session-created-at');
    const sessionOwnerEl = $('#session-owner');
    const sessionRemainingAsteroidsEl = $('#session-remaining-asteroids');
    const sessionTotalAsteroidsEl = $('#session-total-asteroids');
    const sessionProgressBarEl = $('#session-progress-bar');
    const sessionProgressionEl = $('#session-progression');
    const sessionLastScanEl = $('#session-last-scan');
    const sessionFirstScanEl = $('#session-first-scan');
    const sessionFinishTimeEl = $('#session-finish-time');
    const sessionBeltSizeEl = $('#session-belt-size');
    const sessionSpeedEl = $('#session-speed');
    const sessionEtaEl = $('#session-eta');
    /* Chart Element */
    const chartEl = $('#chart');
    /* Apex chart instance */
    let miningChart = null;
    /* Modals */
    const modalRequestDeleteSnapshot = $('#beltradar-accept-delete-snapshot');
    const modalRequestDeleteSurvey = $('#beltradar-accept-delete-survey-session');
    const modalRequestAddSurvey = $('#beltradar-add-survey');
    const modalRequestDeleteBeltTimer = $('#beltradar-accept-delete-belt-timer');
    const modalRequestAddBeltTimer = $('#beltradar-add-belt-timer');

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


    /* Initial Data Fetch */
    fetchGetBeltRadar({
        url: aaBeltRadarSettings.url.surveySessionEntry,
    })
        .then((data) => {
        // Render DataTable with API response data, ensuring entries is an array to prevent errors and providing a fallback empty array if not present
            const entries = Array.isArray(data?.entries) ? data.entries : [];
            BeltRadarSessionsDataTable.clear().rows.add(entries).draw();

            // Update the last snapshot timestamp in the heading, ensuring timestamp is present in the response to prevent errors and providing a fallback message if not available
            if (data?.session?.last_entry_timestamp) {
                $('#ore-survey-heading').html(`${aaBeltRadarSettings.translations.oreSurveyHeading} - ${moment(data.session.last_entry_timestamp).utc().format('YYYY-MM-DD HH:mm:ss')} - ${data.delete_html ?? ''}`);
            }

            // Render Mining Chart with the same data if available, otherwise try to find it in the root of the response
            const chartData = data?.data?.charts ?? data?.charts ?? { categories: [], series: [] };
            renderMiningChart(chartData);
            updateSessionStats(data);
        })
        .catch((error) => {
            console.error('Error fetching Survey Sessions DataTable:', error);
            // Clear the DataTable to show no data and remove loading state
            BeltRadarSessionsDataTable.clear().draw();
            // Show error message in chart area if chart data is not available
            chartEl.html(`<div class="text-muted text-center p-4">${aaBeltRadarSettings.translations.noData}</div>`);
        });

    /**
    * DataTable for Belt Radar Session Entries
    * Initialized empty and filled after async fetch.
    */
    const BeltRadarSessionsDataTable = new DataTable(BeltRadarSessionEntryTable, {
        data: [],
        language: aaBeltRadarSettings.dataTables.language,
        layout: aaBeltRadarSettings.dataTables.layout,
        ordering: aaBeltRadarSettings.dataTables.ordering,
        columnControl: aaBeltRadarSettings.dataTables.columnControl,
        order: [[4, 'desc']],
        columnDefs: [
            {
                orderable: false,
                targets: 0,
                columnControl: [
                    {target: 0, content: []},
                    {target: 1, content: []}
                ]
            },
            {
                targets: [2,3,4,5],
                type: 'num'
            },
        ],
        columns: [
            {
                data: {
                    display: (data) => data.portrait,
                    sort: (data) => data.name,
                    filter: (data) => data.name,
                }
            },
            {
                data: {
                    display: (data) => data.name,
                    sort: (data) => data.name,
                    filter: (data) => data.name,
                }
            },
            {
                data: {
                    display: (data) => `${data.units.toLocaleString()}`,
                    sort: (data) => data.units,
                    filter: (data) => data.units,
                }
            },
            {
                data: {
                    display: (data) => `${data.volume_m3.toLocaleString()} m³`,
                    sort: (data) => data.volume_m3,
                    filter: (data) => data.volume_m3,
                }
            },
            {
                data: {
                    display: (data) => numberFormatter({
                        value: data.price_isk,
                        language: aaBeltRadarSettings.locale,
                        options: {
                            style: 'currency',
                            currency: 'ISK',
                            maximumFractionDigits: 0
                        }
                    }),
                    sort: (data) => data.price_isk,
                    filter: (data) => data.price_isk,
                }
            },
            {
                data: {
                    display: (data) => numberFormatter({
                        value: data.price_compressed,
                        language: aaBeltRadarSettings.locale,
                        options: {
                            style: 'currency',
                            currency: 'ISK',
                            maximumFractionDigits: 0
                        }
                    }),
                    sort: (data) => data.price_compressed,
                    filter: (data) => data.price_compressed,
                }
            },
            {
                data: {
                    display: (data) => numberFormatter({
                        value: data.income_cmp_per_h,
                        language: aaBeltRadarSettings.locale,
                        options: {
                            style: 'currency',
                            currency: 'ISK',
                            maximumFractionDigits: 0
                        }
                    }),
                    sort: (data) => data.income_cmp_per_h,
                    filter: (data) => data.income_cmp_per_h,
                }
            },
        ],
        drawCallback: function () {
            _bootstrapTooltip();
        },
    });

    /* Helper function to format numbers with locale and options, providing a default value of 0 for invalid inputs */
    const formatWholeNumber = (value) => numberFormatter({
        value: Number(value) || 0,
        language: aaBeltRadarSettings.locale,
        options: {
            maximumFractionDigits: 0,
        }
    });

    /* Helper function to format timestamps or return 'N/A' if value is not present */
    const formatTimeOrNA = (value) => (value ? moment(value).utc().format('HH:mm') : 'N/A');

    /* Function to update session stats in the heading based on the latest snapshot data */
    const updateSessionStats = (tableData) => {
        const stats = tableData?.stats ?? {};
        const firstEntryTimestamp = tableData?.session?.first_entry_timestamp ?? null;
        const lastSnapshotTimestamp = tableData?.session?.last_entry_timestamp ?? null;

        sessionNameEl.text(tableData?.session?.name ?? '-');
        sessionCreatedAtEl.text(tableData?.session?.created_at ? moment(tableData.session.created_at).utc().format('YYYY-MM-DD HH:mm:ss') : '-');
        sessionOwnerEl.text(tableData?.session?.owner ?? '-');

        sessionRemainingAsteroidsEl.text(formatWholeNumber(stats.remaining_asteroids));
        sessionTotalAsteroidsEl.text(formatWholeNumber(stats.total_asteroids));

        const progressPercent = Math.max(0, Math.min(100, Number(stats.progress_percent) || 0));
        sessionProgressBarEl.css('width', `${progressPercent}%`);
        sessionProgressBarEl.attr('aria-valuenow', progressPercent.toFixed(2));
        sessionProgressionEl.text(`(${progressPercent.toFixed(0)}%)`);

        const lastScanLabel = sessionLastScanEl.data('last-scan-label') || aaBeltRadarSettings.translations.lastScan;
        const lastScanText = formatTimeOrNA(lastSnapshotTimestamp);
        sessionLastScanEl.text(lastScanText === 'N/A' ? '' : lastScanText);
        sessionLastScanEl.attr('title', `${lastScanLabel}: ${lastScanText}`);

        sessionFirstScanEl.text(formatTimeOrNA(firstEntryTimestamp));
        sessionFinishTimeEl.text(formatTimeOrNA(stats.finish_eta));

        sessionBeltSizeEl.text(`${formatWholeNumber(stats.belt_volume_left_m3)} / ${formatWholeNumber(stats.belt_volume)} m³`);
        sessionSpeedEl.text(`${formatWholeNumber(stats.mining_rate_m3_per_s)} m³/s`);
        sessionEtaEl.text(stats.finish_eta ? moment(stats.finish_eta).fromNow() : 'N/A');
    };

    /**
    * Render Mining Chart using ApexCharts
    * @param {Object} chartData - The data for the chart, expected to have categories and series properties
    */
    const renderMiningChart = (chartData) => {
        if (miningChart) {
            miningChart.destroy();
            miningChart = null;
        }

        // Clear existing chart or messages before rendering new chart
        chartEl.empty();

        if (!Array.isArray(chartData.categories) || chartData.categories.length === 0) {
            console.warn('No categories available for mining chart. Chart will not be rendered.');
            chartEl.html(`<div class="text-muted text-center p-4 w-100">${aaBeltRadarSettings.translations.noData}</div>`);
            return;
        }

        const options = {
            series: Array.isArray(chartData.series) ? chartData.series : [],
            chart: {
                type: 'bar',
                height: 380,
                toolbar: { show: false }
            },
            plotOptions: {
                bar: {
                    borderRadius: 4,
                    borderRadiusApplication: 'end',
                    horizontal: true,
                    dataLabels: {
                        position: 'right'
                    }
                }
            },
            dataLabels: {
                enabled: true,
                formatter: (value) => `${Number(value).toFixed(1)}%`
            },
            xaxis: {
                categories: chartData.categories,
                min: 0,
                max: 100,
                tickAmount: 5,
                labels: {
                    formatter: (value) => `${Number(value).toFixed(0)}%`
                }
            },
            tooltip: {
                y: {
                    formatter: (value) => `${Number(value).toFixed(2)}%`
                }
            },
            theme: {
                mode: 'dark',
            },
        };
        miningChart = new ApexCharts(chartEl[0], options);
        miningChart.render();
    };

    /**
    * View :: Reload Survey Snapshot Function
    * On Confirmation send a request to the API Endpoint, reload the Survey Snapshot DataTable, close the modal
    * @param {string} url - The API Endpoint URL to send the delete request to returns {Promise}
    * @returns {Promise} - A Promise that resolves when the API request is complete
    */
    const _reloadSurveySnapshotData = (tableData) => {
        const dt = BeltRadarSessionEntryTable.DataTable();
        const entries = Array.isArray(tableData?.entries) ? tableData.entries : [];
        dt.clear().rows.add(entries).draw();
        if (tableData?.session?.last_entry_timestamp) {
            $('#ore-survey-heading').html(`${aaBeltRadarSettings.translations.oreSurveyHeading} - ${moment(tableData.session.last_entry_timestamp).utc().format('YYYY-MM-DD HH:mm:ss')} - ${tableData.delete_html ?? ''} ${tableData.add_survey ?? ''}`);
        } else {
            $('#ore-survey-heading').html(`${aaBeltRadarSettings.translations.oreSurveyHeading} - N/A`);
        }
        BeltRadarSessionEntryTable.addClass('highlight');
        sessionContainer.addClass('highlight');
        chartEl.addClass('highlight');

        setTimeout(() => {
            BeltRadarSessionEntryTable.removeClass('highlight');
            sessionContainer.removeClass('highlight');
            chartEl.removeClass('highlight');
        }, 2000);

        const chartData = tableData?.data?.charts ?? tableData?.charts ?? { categories: [], series: [] };
        renderMiningChart(chartData);
        updateSessionStats(tableData);
    };

    /**
    * Table :: Snapshots :: Delete Button Click Handler
    * Open Delete Snapshot Modal
    * On Confirmation send a request to the API Endpoint, reload the Snapshots DataTable, close the modal
    * and reopen the previous Snapshots Modal
    */
    modalRequestDeleteSnapshot.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('action');
        const form = modalRequestDeleteSnapshot.find('form');
        const csrfMiddlewareToken = form.find('input[name="csrfmiddlewaretoken"]').val();

        modalRequestDeleteSnapshot.find('#modal-button-confirm-accept-request').on('click', () => {
            fetchPostBeltRadar({
                url: url,
                csrfToken: csrfMiddlewareToken,
                payload: {}
            })
                .then((data) => {
                    if (data.success === true) {
                        fetchGetBeltRadar({
                            url: aaBeltRadarSettings.url.surveySessionEntry,
                        })
                            .then((newData) => {
                                _reloadSurveySnapshotData(newData);
                                modalRequestDeleteSnapshot.modal('hide');
                            })
                            .catch((error) => {
                                console.error('Error fetching Survey Snapshot DataTable:', error);
                            });
                    }
                })
                .catch((error) => {
                    console.error(`Error posting delete request: ${error.message}`);
                });
        });
    })
        .on('hide.bs.modal', () => {
            modalRequestDeleteSnapshot.find('#modal-button-confirm-accept-request').unbind('click');
        });

    _bootstrapTooltip();

    /**
    * View :: Survey Sessions :: Delete Button Click Handler
    * Open Delete Survey Session Modal
    * On Confirmation send a request to the API Endpoint, reload the Survey Sessions DataTable, close the modal
    * and reopen the previous Survey Sessions Modal
    */
    modalRequestDeleteSurvey.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('action');
        const form = modalRequestDeleteSurvey.find('form');
        const csrfMiddlewareToken = form.find('input[name="csrfmiddlewaretoken"]').val();

        modalRequestDeleteSurvey.find('#modal-button-confirm-accept-request').on('click', () => {
            modalRequestDeleteSurvey.find('#beltradar-spinner').removeClass('d-none');
            modalRequestDeleteSurvey.find('#beltradar-error').addClass('d-none').removeClass('br-shake').text('');
            fetchPostBeltRadar({
                url: url,
                csrfToken: csrfMiddlewareToken,
                payload: {}
            })
                .then((data) => {
                    if (data.success === true) {
                        modalRequestDeleteSurvey.modal('hide');
                        window.location.href = aaBeltRadarSettings.url.index;
                    }
                })
                .catch((error) => {
                    console.error(`Error posting delete request: ${error.message}`);
                    modalRequestDeleteSurvey.find('#beltradar-error').text(error.message).removeClass('d-none').addClass('br-shake');
                });
        });
    })
        .on('hide.bs.modal', () => {
            modalRequestDeleteSurvey.find('#modal-button-confirm-accept-request').unbind('click');
            modalRequestDeleteSurvey.find('#beltradar-error').addClass('d-none').removeClass('br-shake').text('');
        });

    /**
    * View :: Survey Sessions :: Add Survey Button Click Handler
    * Open Add Survey Modal
    * On Confirmation send a request to the API Endpoint, reload the Survey Sessions DataTable, close the modal
    * and reopen the previous Survey Sessions Modal
    */
    modalRequestAddSurvey.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('action');
        const form = modalRequestAddSurvey.find('form');
        const nativeForm = form.get(0);
        const csrfMiddlewareToken = form.find('input[name="csrfmiddlewaretoken"]').val();
        const formTextArea = form.find('textarea[name="raw_data"]');

        modalRequestAddSurvey.find('#modal-button-confirm-add-request').on('click', () => {
            // This modal uses a regular button + fetch, so enforce HTML5 validation manually.
            formTextArea.prop('required', true);

            if (nativeForm && !nativeForm.checkValidity()) {
                nativeForm.reportValidity();
                return;
            }

            modalRequestAddSurvey.find('#beltradar-spinner').removeClass('d-none');
            modalRequestAddSurvey.find('#beltradar-error').addClass('d-none').removeClass('br-shake').text('');
            const rawData = formTextArea.val();
            fetchPostBeltRadar({
                url: url,
                csrfToken: csrfMiddlewareToken,
                payload: {
                    raw_data: rawData,
                }
            })
                .then((data) => {
                    if (data.success === true) {
                        fetchGetBeltRadar({
                            url: aaBeltRadarSettings.url.surveySessionEntry,
                        })
                            .then((freshData) => {
                                _reloadSurveySnapshotData(freshData);
                                modalRequestAddSurvey.modal('hide');
                            })
                            .catch((error) => {
                                console.error('Error fetching Survey Snapshot DataTable after add:', error);
                                modalRequestAddSurvey.find('#beltradar-error').text(error.message).removeClass('d-none').addClass('br-shake');
                            });
                    }
                })
                .catch((error) => {
                    console.error(`Error posting add survey request: ${error.message}`);
                    modalRequestAddSurvey.find('#beltradar-error').text(error.message).removeClass('d-none').addClass('br-shake');
                })
                .finally(() => {
                    modalRequestAddSurvey.find('#beltradar-spinner').addClass('d-none');
                });
        });
    })
        .on('hide.bs.modal', () => {
            modalRequestAddSurvey.find('#modal-button-confirm-add-request').unbind('click');
            modalRequestAddSurvey.find('textarea[name="raw_data"]').val('');
            modalRequestAddSurvey.find('#beltradar-spinner').addClass('d-none');
            modalRequestAddSurvey.find('#beltradar-error').addClass('d-none').removeClass('br-shake').text('');
        });


    /**
    * DataTable for Belt Radar Session - Belt Timer
    * Initialized empty and filled after async fetch.
    */
    const BeltRadarBeltTimerDataTable = new DataTable(BeltRadarBeltTimerTable, {
        data: [],
        language: aaBeltRadarSettings.dataTables.language,
        layout: aaBeltRadarSettings.dataTables.layout,
        ordering: aaBeltRadarSettings.dataTables.ordering,
        columnControl: aaBeltRadarSettings.dataTables.columnControl,
        order: [[2, 'desc']],
        columnDefs: [],
        columns: [
            {
                data: {
                    display: (data) => data.public_id,
                    sort: (data) => data.public_id,
                    filter: (data) => data.public_id,
                }
            },
            {
                data: {
                    display: (data) => data.belt_id,
                    sort: (data) => data.belt_id,
                    filter: (data) => data.belt_id,
                }
            },
            {
                data: {
                    display: (data) => data.belt_name,
                    sort: (data) => data.belt_name,
                    filter: (data) => data.belt_name,
                }
            },
            {
                data: {
                    display: (data) => data.belt_size,
                    sort: (data) => data.belt_size,
                    filter: (data) => data.belt_size,
                }
            },
            {
                data: {
                    display: (data) => data.belt_type,
                    sort: (data) => data.belt_type,
                    filter: (data) => data.belt_type,
                }
            },
            {
                data: {
                    display: (data) => moment(data.eta).format('YYYY-MM-DD HH:mm:ss'),
                    sort: (data) => data.eta,
                    filter: (data) => data.eta,
                }
            },
            {
                data: {
                    display: (data) => data.html,
                    sort: (data) => data.html,
                    filter: (data) => data.html,
                }
            },
        ],
        initComplete: function() {
            _bootstrapTooltip({selector: '#beltradar-belt-timer-table'});
        },
        drawCallback: function () {
            _bootstrapTooltip({selector: '#beltradar-belt-timer-table'});
        },
    });

    fetchGetBeltRadar({
        url: aaBeltRadarSettings.url.userBeltTimer,
    })
        .then((data) => {
            BeltRadarBeltTimerDataTable.clear().rows.add(data).draw();
        })
        .catch((error) => {
            console.error('Error fetching User Belt Timer DataTable:', error);
            BeltRadarBeltTimerDataTable.clear().draw();
        });

    /**
    * View :: Reload Belt Timer Function
    * On Confirmation send a request to the API Endpoint, reload the Belt Timer DataTable, close the modal
    * @param {string} url - The API Endpoint URL to send the delete request to returns {Promise}
    * @returns {Promise} - A Promise that resolves when the API request is complete
    */
    const _reloadSurveyBeltTimerData = (tableData) => {
        const dt = BeltRadarBeltTimerTable.DataTable();
        dt.clear().rows.add(tableData).draw();
        BeltRadarBeltTimerTable.addClass('highlight');

        setTimeout(() => {
            BeltRadarBeltTimerTable.removeClass('highlight');
        }, 2000);
    };


    /**
    * View :: Belt Timer :: Add Belt Timer Button Click Handler
    * Open Add Belt Timer Modal
    * On Confirmation send a request to the API Endpoint, reload the Belt Timer DataTable, close the modal
    * and reopen the previous Belt Timer Modal
    */
    modalRequestAddBeltTimer.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('action');
        const form = modalRequestAddBeltTimer.find('form');
        const nativeForm = form.get(0);
        const csrfMiddlewareToken = form.find('input[name="csrfmiddlewaretoken"]').val();
        const beltIdInput = form.find('input[name="belt_id"]');
        const beltNameInput = form.find('input[name="belt_name"]');
        const beltTypeSelect = form.find('select[name="belt_type"]');
        const beltSizeSelect = form.find('select[name="belt_size"]');

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

        const updateBeltSizeChoices = () => {
            const selectedType = beltTypeSelect.val();
            const allowedChoices = sizeChoices[selectedType] || [
                ['small', 'Small'],
                ['medium', 'Medium'],
                ['large', 'Large'],
                ['enormous', 'Enormous'],
                ['colossal', 'Colossal'],
                ['ice', 'Ice'],
            ];
            const previousValue = beltSizeSelect.val();

            beltSizeSelect.empty();

            allowedChoices.forEach(([value, label]) => {
                beltSizeSelect.append(
                    $('<option></option>')
                        .attr('value', value)
                        .text(label)
                );
            });

            const hasPreviousValue = allowedChoices.some(([value]) => value === previousValue);
            beltSizeSelect.val(hasPreviousValue ? previousValue : (allowedChoices[0]?.[0] || ''));
        };

        beltTypeSelect.off('change.brBeltTimer').on('change.brBeltTimer', updateBeltSizeChoices);
        updateBeltSizeChoices();

        modalRequestAddBeltTimer.find('#modal-button-confirm-add-request').on('click', () => {
            if (nativeForm && !nativeForm.checkValidity()) {
                nativeForm.reportValidity();
                return;
            }

            modalRequestAddBeltTimer.find('#beltradar-spinner').removeClass('d-none');
            modalRequestAddBeltTimer.find('#beltradar-error').addClass('d-none').removeClass('br-shake').text('');
            fetchPostBeltRadar({
                url: url,
                csrfToken: csrfMiddlewareToken,
                payload: {
                    belt_id: beltIdInput.val(),
                    belt_name: beltNameInput.val(),
                    belt_type: beltTypeSelect.val(),
                    belt_size: beltSizeSelect.val(),
                }
            })
                .then((data) => {
                    if (data.success === true) {
                        fetchGetBeltRadar({
                            url: aaBeltRadarSettings.url.userBeltTimer,
                        })
                            .then((freshData) => {
                                _reloadSurveyBeltTimerData(freshData);
                                modalRequestAddBeltTimer.modal('hide');
                            })
                            .catch((error) => {
                                console.error('Error fetching Survey Snapshot DataTable after add:', error);
                                modalRequestAddBeltTimer.find('#beltradar-error').text(error.message).removeClass('d-none').addClass('br-shake');
                            });
                    }
                })
                .catch((error) => {
                    console.error(`Error posting add survey belt timer request: ${error.message}`);
                    modalRequestAddBeltTimer.find('#beltradar-error').text(error.message).removeClass('d-none').addClass('br-shake');
                })
                .finally(() => {
                    modalRequestAddBeltTimer.find('#beltradar-spinner').addClass('d-none');
                });
        });
    })
        .on('hide.bs.modal', () => {
            modalRequestAddBeltTimer.find('#modal-button-confirm-add-request').unbind('click');
            modalRequestAddBeltTimer.find('input[name="belt_id"]').val('');
            modalRequestAddBeltTimer.find('input[name="belt_name"]').val('');
            modalRequestAddBeltTimer.find('select[name="belt_type"]').off('change.brBeltTimer');
            modalRequestAddBeltTimer.find('select[name="belt_type"]').val('');
            modalRequestAddBeltTimer.find('select[name="belt_size"]').val('');
            modalRequestAddBeltTimer.find('#beltradar-spinner').addClass('d-none');
            modalRequestAddBeltTimer.find('#beltradar-error').addClass('d-none').removeClass('br-shake').text('');
        });

});
