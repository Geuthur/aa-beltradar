/* global aaBeltRadarSettings, aaBeltRadarSettingsOverride, _bootstrapTooltip, DataTable, numberFormatter, moment, ApexCharts, fetchGetBeltRadar, fetchPostBeltRadar */

$(document).ready(() => {
    /* DataTable for Belt Radar Session Entries */
    const BeltRadarSessionEntryTable = $('#beltradar-session-entry-table');
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
    const trafficChartEl = $('#traffic');
    /* Apex chart instance */
    let miningChart = null;
    let trafficChart = null;
    /* Modals */
    const modalRequestDeleteSnapshot = $('#beltradar-accept-delete-snapshot');
    const modalRequestDeleteSurvey = $('#beltradar-accept-delete-survey-session');
    const modalRequestAddSurvey = $('#beltradar-add-survey');

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
            const trafficChartData = data?.data?.traffic ?? data?.traffic ?? { categories: [], series: [] };
            renderTrafficChart(trafficChartData);
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

    /* Keep Bootstrap tooltip source attributes in sync when values change after initialisation. */
    const setTooltipTitle = (element, title) => {
        element.attr('title', title);
        element.attr('data-bs-original-title', title);
        element.attr('data-bs-tooltip', 'aa-beltradar');
    };

    /* Function to update session stats in the heading based on the latest snapshot data */
    const updateSessionStats = (tableData) => {
        const stats = tableData?.stats ?? {};
        let firstEntryTimestamp = tableData?.session?.first_entry_timestamp ?? null;
        let lastSnapshotTimestamp = tableData?.session?.last_entry_timestamp ?? null;

        sessionNameEl.text(tableData?.session?.name ?? '-');
        sessionCreatedAtEl.text(tableData?.session?.created_at ? moment(tableData.session.created_at).utc().format('YYYY-MM-DD HH:mm:ss') : '-');
        sessionOwnerEl.text(tableData?.session?.owner ?? '-');

        sessionRemainingAsteroidsEl.text(formatWholeNumber(stats.remaining_asteroids));
        sessionTotalAsteroidsEl.text(formatWholeNumber(stats.total_asteroids));

        const progressPercent = Math.max(0, Math.min(100, Number(stats.progress_percent) || 0));
        sessionProgressBarEl.css('width', `${progressPercent}%`);
        sessionProgressBarEl.attr('aria-valuenow', progressPercent.toFixed(2));
        sessionProgressionEl.text(`(${progressPercent.toFixed(0)}%)`);

        /* Update first and last scan timestamps with tooltips */
        const firstScanLabel = aaBeltRadarSettings.translations.firstScan;
        let firstScanText = formatTimeOrNA(firstEntryTimestamp);
        sessionFirstScanEl.text(firstScanText);
        setTooltipTitle(sessionFirstScanEl, `${firstScanLabel}: ${firstScanText}`);

        const lastScanLabel = aaBeltRadarSettings.translations.lastScan;
        let lastScanText = formatTimeOrNA(lastSnapshotTimestamp);
        /* If the last snapshot timestamp is the same as the first entry timestamp, clear the text. */
        if (lastSnapshotTimestamp === firstEntryTimestamp) {
            sessionLastScanEl.text('');
        } else {
            sessionLastScanEl.text(lastScanText);
            setTooltipTitle(sessionLastScanEl, `${lastScanLabel}: ${lastScanText}`);
        }

        sessionFinishTimeEl.text(formatTimeOrNA(stats.finish_eta));

        sessionBeltSizeEl.text(`${formatWholeNumber(stats.belt_volume_left_m3)} / ${formatWholeNumber(stats.belt_volume)} m³`);
        sessionSpeedEl.text(`${formatWholeNumber(stats.mining_rate_m3_per_s)} m³/s`);
        sessionEtaEl.text(stats.finish_eta ? moment(stats.finish_eta).fromNow() : 'N/A');
        _bootstrapTooltip();
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
    * Render Traffic Chart using ApexCharts
    * @param {Object} chartData - The data for the chart, expected to have categories and series properties
    */
    const renderTrafficChart = (chartData) => {
        if (trafficChart) {
            trafficChart.destroy();
            trafficChart = null;
        }

        // Clear existing chart or messages before rendering new chart
        trafficChartEl.empty();

        if (!Array.isArray(chartData.categories) || chartData.categories.length === 0) {
            console.warn('No categories available for traffic chart. Chart will not be rendered.');
            trafficChartEl.html(`<div class="text-muted text-center p-4 w-100">${aaBeltRadarSettings.translations.noData}</div>`);
            return;
        }

        const options = {
            series: Array.isArray(chartData.series) ? chartData.series : [],
            chart: {
                type: 'line',
                height: 380,
                toolbar: { show: false }
            },
            stroke: {
                width: [0, 4],
                curve: 'smooth',
            },
            title: {
                text: 'Mining Speed',
            },
            dataLabels: {
                enabled: true,
                enabledOnSeries: [1],
                formatter: function (val) {
                    return val.toLocaleString() + ' m³/s';
                },
            },
            labels: Array.isArray(chartData.categories) ? chartData.categories : [],
            yaxis: [
                {
                    title: {
                        text: 'Volume Left (m³)',
                    },
                },
                {
                    opposite: true,
                    title: {
                        text: 'Speed (m³/s)',
                    },
                },
            ],
            tooltip: {
                shared: true,
                intersect: false,
                y: {
                    formatter: function (val, { seriesIndex }) {
                        if (seriesIndex === 0) {
                            return val.toLocaleString() + ' m³';
                        } else if (seriesIndex === 1) {
                            return val.toLocaleString() + ' m³/s';
                        }
                        return val;
                    },
                },
            },
            theme: {
                mode: 'dark',
            },
        };
        trafficChart = new ApexCharts(trafficChartEl[0], options);
        trafficChart.render();
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
        const trafficChartData = tableData?.data?.traffic ?? tableData?.traffic ?? { categories: [], series: [] };
        renderTrafficChart(trafficChartData);
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

});
