/* global aaBeltRadarSettings, aaBeltRadarSettingsOverride, _bootstrapTooltip, DataTable, numberFormatter, moment, ApexCharts, fetchGetBeltRadar, fetchPostBeltRadar, renderMiningChart, renderTrafficChart, chartContainer, trafficChartContainer */

$(document).ready(() => {
    // DataTable for Belt Radar Session Entries
    const BeltRadarSessionSnapshotTable = $('#beltradar-session-entry-table');

    // Session details elements
    const sessionContainer = $('#session-details-container');
    const sessionName = $('#session-name');
    const sessionCreatedAt = $('#session-created-at');
    const sessionOwner = $('#session-owner');
    const sessionRemainingAsteroids = $('#session-remaining-asteroids');
    const sessionTotalAsteroids = $('#session-total-asteroids');
    const sessionProgressBar = $('#session-progress-bar');
    const sessionProgression = $('#session-progression');
    const sessionLastScan = $('#session-last-scan');
    const sessionFirstScan = $('#session-first-scan');
    const sessionFinishTime = $('#session-finish-time');
    const sessionTotalTimestamps = $('#session-total-survey-entries');
    const sessionBeltSize = $('#session-belt-size');
    const sessionSpeed = $('#session-speed');
    const sessionEta = $('#session-eta');
    const sessionExpectedBeltType = $('#session-expected-belt-type');
    const sessionExpectedBeltSize = $('#session-expected-belt-size');
    const sessionBeltTimer = $('#session-belt-timer');

    // Modals
    const modalRequestDeleteSnapshot = $('#beltradar-accept-delete-snapshot');
    const modalRequestDeleteSession = $('#beltradar-accept-delete-session');
    const modalRequestAddSnapshot = $('#beltradar-add-snapshot');
    const modalRequestCreateTimer = $('#beltradar-accept-create-belt-timer');
    const modalRequestDeleteBeltTimer = $('#beltradar-accept-delete-belt-timer');

    // Apex chart instance
    let miningChart = null;
    let trafficChart = null;

    // Chart Element
    const chartContainer = $('#chart');
    const trafficChartContainer = $('#traffic');

    /**
    * DataTable for Belt Radar Session Entries
    * Initialized empty and filled after async fetch.
    */
    const BeltRadarSessionsDataTable = new DataTable(BeltRadarSessionSnapshotTable, {
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

    // Helper function to format numbers with locale and options, providing a default value of 0 for invalid inputs
    const formatWholeNumber = (value) => numberFormatter({
        value: Number(value) || 0,
        language: aaBeltRadarSettings.locale,
        options: {
            maximumFractionDigits: 0,
        }
    });

    // Helper function to format timestamps or return 'N/A' if value is not present
    const formatTimeOrNA = (value) => (value ? moment(value).utc().format('HH:mm') : 'N/A');

    // Keep Bootstrap tooltip source attributes in sync when values change after initialisation.
    const setTooltipTitle = (element, title) => {
        element.attr('title', title);
        element.attr('data-bs-original-title', title);
    };

    // Highlight function
    const highlightElement = (element, duration = 2000) => {
        element.addClass('highlight');
        setTimeout(() => {
            element.removeClass('highlight');
        }, duration);
    };

    /**
    * View :: Fetch Snapshot Data Function
    * Fetches the latest snapshot data from the API and updates the DataTable and charts accordingly.
    * @param {string} snapshotUrl - The API Endpoint URL to fetch the snapshot data from. Returns {Promise}
    * @returns {void} - Updates the DataTable and charts directly
    */
    const _fetchSnapshotData = (snapshotUrl = aaBeltRadarSettings.url.surveySessionEntry) => {
        fetchGetBeltRadar({
            url: snapshotUrl,
        })
            .then((snapshotData) => {
                const dt = BeltRadarSessionSnapshotTable.DataTable();
                const ore_list = Array.isArray(snapshotData?.ore_list) ? snapshotData.ore_list : [];

                // Clear the DataTable and add new entries, ensuring entries is an array to prevent errors and providing a fallback empty array if not present
                dt.clear().rows.add(ore_list).draw();

                // Update the last snapshot timestamp in the heading, ensuring timestamp is present in the response to prevent errors and providing a fallback message if not available
                if (snapshotData?.snapshot?.last_timestamp) {
                    $('#ore-snapshot-heading').html(`${aaBeltRadarSettings.translations.lastSnapshot} - ${moment(snapshotData?.snapshot?.last_timestamp).utc().format('YYYY-MM-DD HH:mm:ss')} - ${snapshotData.actions.delete ?? ''}`);
                } else {
                    $('#ore-snapshot-heading').html(`${aaBeltRadarSettings.translations.lastSnapshot} - N/A`);
                }

                // Render Mining Chart with the same data if available, otherwise try to find it in the root of the response
                _reloadCharts(snapshotData);
                _fetchSessionData();
            })
            .catch((error) => {
                console.error('Error fetching snapshot data:', error);
                BeltRadarSessionsDataTable.clear().draw();
                // Show error message in chart area if chart data is not available
                chartContainer.html(`<div class="text-muted text-center p-4">${aaBeltRadarSettings.translations.noData}</div>`);
                trafficChartContainer.html(`<div class="text-muted text-center p-4">${aaBeltRadarSettings.translations.noData}</div>`);
            });
    };

    /**
     * View :: Fetch Session Data Function
     * Fetches the latest session data from the API and updates the session details and charts accordingly.
     * If no URL is provided, it defaults to aaBeltRadarSettings.url.sessionData.
     * @param {string} sessionDataOrUrl - The session data object or the URL to fetch the session data from. If not provided, defaults to aaBeltRadarSettings.url.sessionData.
     * @returns {void} - Updates the session details and charts directly
     *
     */
    const _fetchSessionData = (sessionDataOrUrl = aaBeltRadarSettings.url.sessionData) => {
        fetchGetBeltRadar({
            url: sessionDataOrUrl,
        })
            .then((sessionData) => {
                const stats = sessionData?.stats ?? {};
                const now = moment();
                let firstSnapshotTimestamp = sessionData?.first_timestamp ?? null;
                let lastSnapshotTimestamp = sessionData?.last_timestamp ?? null;
                let finishEta = stats?.finish_eta ?? null;
                // Use moment to parse finishEta for comparison and formatting
                const finishMoment = moment(finishEta);

                // Create Timer Button HTML and insert it into the session-belt-timer container
                const createTimerHtml = sessionData?.actions?.create ?? '';
                sessionBeltTimer.html(createTimerHtml);

                sessionName.text(sessionData?.name ?? '-');
                sessionCreatedAt.text(sessionData?.created_at ? moment(sessionData.created_at).utc().format('YYYY-MM-DD HH:mm:ss') : '-');
                sessionOwner.text(sessionData?.owner ?? '-');

                sessionRemainingAsteroids.text(formatWholeNumber(stats.remaining_asteroids));
                sessionTotalAsteroids.text(formatWholeNumber(stats.total_asteroids));

                const progressPercent = Math.max(0, Math.min(100, Number(stats.progress_percent) || 0));
                sessionProgressBar.css('width', `${progressPercent}%`);
                sessionProgressBar.attr('aria-valuenow', progressPercent.toFixed(2));
                sessionProgression.text(`(${progressPercent.toFixed(0)}%)`);
                sessionContainer.toggleClass('session-progress-near-complete', progressPercent >= 90);

                // Update first and last scan timestamps with tooltips
                const firstScanLabel = aaBeltRadarSettings.translations.firstScan;
                let firstScanText = formatTimeOrNA(firstSnapshotTimestamp);
                sessionFirstScan.text(firstScanText);
                setTooltipTitle(sessionFirstScan, `${firstScanLabel}: ${firstScanText}`);

                // Update last scan timestamp with tooltip, but clear the text if it's the same as the first entry timestamp
                const lastScanLabel = aaBeltRadarSettings.translations.lastScan;
                let lastScanText = formatTimeOrNA(lastSnapshotTimestamp);
                // If the last snapshot timestamp is the same as the first entry timestamp, clear the text.
                if (lastSnapshotTimestamp === firstSnapshotTimestamp) {
                    sessionLastScan.text('');
                } else {
                    sessionLastScan.text(lastScanText);
                    setTooltipTitle(sessionLastScan, `${lastScanLabel}: ${lastScanText}`);
                }

                // Update finish time and ETA with tooltips
                const finishTimeLabel = aaBeltRadarSettings.translations.etaScan;
                let finishTimeText = formatTimeOrNA(finishEta);
                sessionFinishTime.text(finishTimeText);
                setTooltipTitle(sessionFinishTime, `${finishTimeLabel}: ${moment(finishEta).utc().format('MMM DD HH:mm:ss')}`);

                // Update total timestamps with tooltip
                sessionTotalTimestamps.text(formatWholeNumber(sessionData?.total_timestamps ?? 0));

                // Update belt size, speed, and ETA
                sessionBeltSize.text(`${formatWholeNumber(stats.belt_volume_left_m3)} / ${formatWholeNumber(stats.belt_volume)} m³`);
                sessionSpeed.text(`${formatWholeNumber(stats.mining_rate_m3_per_s)} m³/s`);

                // Update ETA text based on whether the finish time is in the past or future
                if (finishEta) {
                    if (finishMoment.isBefore(now)) {
                        sessionEta.text(aaBeltRadarSettings.translations.etaPassed);
                    } else {
                        sessionEta.text(moment(stats.finish_eta).fromNow());
                    }
                }

                // Update expected belt type and size
                sessionExpectedBeltType.text(stats.expected_belt_type ?? 'N/A');
                sessionExpectedBeltSize.text(stats.expected_belt_size ?? 'N/A');

                // Re-initialize Bootstrap tooltips after updating the DOM elements
                _bootstrapTooltip();
            })
            .catch((error) => {
                console.error('Error fetching session data:', error);
            });
    };

    /**
    * Reload Charts Function
    * @param {Object} tableData - The data for the charts, expected to have charts and traffic properties
    * @returns {void} - Updates the mining and traffic charts directly
    */
    const _reloadCharts = (tableData) => {
        const chartData = tableData?.data?.charts ?? tableData?.charts ?? { categories: [], series: [] };
        renderMiningChart(chartData);
        const trafficChartData = tableData?.data?.traffic ?? tableData?.traffic ?? { categories: [], series: [] };
        renderTrafficChart(trafficChartData);
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
                        _fetchSnapshotData();
                        _fetchSessionData();
                        // Highlight the DataTable and session details container to indicate that new data has been loaded
                        highlightElement(BeltRadarSessionSnapshotTable);
                        highlightElement(sessionContainer);
                        // Close the modal after successful submission
                        modalRequestDeleteSnapshot.modal('hide');
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
    * View :: Session :: Delete Button Click Handler
    * Open Delete Session Modal
    * On Confirmation send a request to the API Endpoint, reload the Session DataTable, close the modal
    * and reopen the previous Sessions Modal
    */
    modalRequestDeleteSession.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('action');
        const form = modalRequestDeleteSession.find('form');
        const csrfMiddlewareToken = form.find('input[name="csrfmiddlewaretoken"]').val();

        modalRequestDeleteSession.find('#modal-button-confirm-accept-request').on('click', () => {
            modalRequestDeleteSession.find('#beltradar-spinner').removeClass('d-none');
            modalRequestDeleteSession.find('#beltradar-error').addClass('d-none').removeClass('br-shake').text('');
            fetchPostBeltRadar({
                url: url,
                csrfToken: csrfMiddlewareToken,
                payload: {}
            })
                .then((data) => {
                    if (data.success === true) {
                        modalRequestDeleteSession.modal('hide');
                        window.location.href = aaBeltRadarSettings.url.index;
                    }
                })
                .catch((error) => {
                    console.error(`Error posting delete request: ${error.message}`);
                    modalRequestDeleteSession.find('#beltradar-error').text(error.message).removeClass('d-none').addClass('br-shake');
                });
        });
    })
        .on('hide.bs.modal', () => {
            modalRequestDeleteSession.find('#modal-button-confirm-accept-request').unbind('click');
            modalRequestDeleteSession.find('#beltradar-error').addClass('d-none').removeClass('br-shake').text('');
        });

    /**
    * View :: Session :: Add Snapshot Button Click Handler
    * Open Add Snapshot Modal
    * On Confirmation send a request to the API Endpoint, reload the Session DataTable, close the modal
    * and reopen the previous Session Modal
    */
    modalRequestAddSnapshot.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('action');
        const form = modalRequestAddSnapshot.find('form');
        const nativeForm = form.get(0);
        const csrfMiddlewareToken = form.find('input[name="csrfmiddlewaretoken"]').val();
        const formTextArea = form.find('textarea[name="raw_data"]');

        modalRequestAddSnapshot.find('#modal-button-confirm-add-request').on('click', () => {
            // This modal uses a regular button + fetch, so enforce HTML5 validation manually.
            formTextArea.prop('required', true);

            if (nativeForm && !nativeForm.checkValidity()) {
                nativeForm.reportValidity();
                return;
            }

            modalRequestAddSnapshot.find('#beltradar-spinner').removeClass('d-none');
            modalRequestAddSnapshot.find('#beltradar-error').addClass('d-none').removeClass('br-shake').text('');
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
                        _fetchSnapshotData();
                        _fetchSessionData();
                        // Highlight the DataTable and session details container to indicate that new data has been loaded
                        highlightElement(BeltRadarSessionSnapshotTable);
                        highlightElement(sessionContainer);
                        // Close the modal after successful submission
                        modalRequestAddSnapshot.modal('hide');
                    }
                })
                .catch((error) => {
                    console.error(`Error posting add Snapshot request: ${error.message}`);
                    modalRequestAddSnapshot.find('#beltradar-error').text(error.message).removeClass('d-none').addClass('br-shake');
                })
                .finally(() => {
                    modalRequestAddSnapshot.find('#beltradar-spinner').addClass('d-none');
                });
        });
    })
        .on('hide.bs.modal', () => {
            modalRequestAddSnapshot.find('#modal-button-confirm-add-request').unbind('click');
            modalRequestAddSnapshot.find('textarea[name="raw_data"]').val('');
            modalRequestAddSnapshot.find('#beltradar-spinner').addClass('d-none');
            modalRequestAddSnapshot.find('#beltradar-error').addClass('d-none').removeClass('br-shake').text('');
        });

    /**
    * View :: Session :: Create Timer Button Click Handler
    * Open Create Belt Timer Modal
    * On Confirmation send a request to the API Endpoint, reload the Session DataTable, close the modal
    */
    modalRequestCreateTimer.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('action');
        const form = modalRequestCreateTimer.find('form');
        const csrfMiddlewareToken = form.find('input[name="csrfmiddlewaretoken"]').val();

        modalRequestCreateTimer.find('#modal-button-confirm-accept-request').on('click', () => {
            modalRequestCreateTimer.find('#beltradar-spinner').removeClass('d-none');
            modalRequestCreateTimer.find('#beltradar-error').addClass('d-none').removeClass('br-shake').text('');
            fetchPostBeltRadar({
                url: url,
                csrfToken: csrfMiddlewareToken,
                payload: {}
            })
                .then((data) => {
                    if (data.success === true) {
                        _fetchSnapshotData();
                        _fetchSessionData();
                        // Highlight the DataTable and session details container to indicate that new data has been loaded
                        highlightElement(BeltRadarSessionSnapshotTable);
                        highlightElement(sessionContainer);
                        // Close the modal after successful submission
                        modalRequestCreateTimer.modal('hide');
                    }
                })
                .catch((error) => {
                    console.error(`Error posting create timer request: ${error.message}`);
                    modalRequestCreateTimer.find('#beltradar-error').text(error.message).removeClass('d-none').addClass('br-shake');
                });
        });
    })
        .on('hide.bs.modal', () => {
            modalRequestCreateTimer.find('#modal-button-confirm-accept-request').unbind('click');
            modalRequestCreateTimer.find('#beltradar-error').addClass('d-none').removeClass('br-shake').text('');
        });

    /**
    * Table :: Belt-Timer :: Delete Button Click Handler
    * Open Delete Belt-Timer Modal
    * On Confirmation send a request to the API Endpoint, reload the Belt-Timer DataTable, close the modal
    * and reopen the previous Belt-Timer Modal
    */
    modalRequestDeleteBeltTimer.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('action');
        const form = modalRequestDeleteBeltTimer.find('form');
        const csrfMiddlewareToken = form.find('input[name="csrfmiddlewaretoken"]').val();

        modalRequestDeleteBeltTimer.find('#modal-button-confirm-accept-request').on('click', () => {
            fetchPostBeltRadar({
                url: url,
                csrfToken: csrfMiddlewareToken,
                payload: {}
            })
                .then((data) => {
                    if (data.success === true) {
                        _fetchSnapshotData();
                        _fetchSessionData();
                        // Highlight the DataTable and session details container to indicate that new data has been loaded
                        highlightElement(BeltRadarSessionSnapshotTable);
                        highlightElement(sessionContainer);
                        // Close the modal after successful submission
                        modalRequestDeleteBeltTimer.modal('hide');
                    }
                })
                .catch((error) => {
                    console.error(`Error posting delete request: ${error.message}`);
                });
        });
    })
        .on('hide.bs.modal', () => {
            modalRequestDeleteBeltTimer.find('#modal-button-confirm-accept-request').unbind('click');
        });

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
        chartContainer.empty();

        if (!Array.isArray(chartData.categories) || chartData.categories.length === 0) {
            console.warn('No categories available for mining chart. Chart will not be rendered.');
            chartContainer.html(`<div class="text-muted text-center p-4 w-100">${aaBeltRadarSettings.translations.noData}</div>`);
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
            title: {
                text: aaBeltRadarSettings.translations.oreProgression,
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
        miningChart = new ApexCharts(chartContainer[0], options);
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
        trafficChartContainer.empty();

        if (!Array.isArray(chartData.categories) || chartData.categories.length === 0) {
            console.warn('No categories available for traffic chart. Chart will not be rendered.');
            trafficChartContainer.html(`<div class="text-muted text-center p-4 w-100">${aaBeltRadarSettings.translations.noData}</div>`);
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
                text: aaBeltRadarSettings.translations.miningSpeed,
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
        trafficChart = new ApexCharts(trafficChartContainer[0], options);
        trafficChart.render();
    };

    // Initial Data Fetch
    _fetchSessionData();
    _fetchSnapshotData();
});
