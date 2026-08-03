/* global aaBeltRadarSettings, aaBeltRadarSettingsOverride, _bootstrapTooltip, DataTable, numberFormatter, moment, ApexCharts, updateBeltSizeChoices, fetchGetBeltRadar, fetchPostBeltRadar */

$(document).ready(() => {
    /* Initialize Bootstrap Tooltips */
    _bootstrapTooltip();
    /* DataTable for Belt Radar Session Entries */
    const BeltRadarSessionTable = $('#beltradar-session-table');
    const BeltRadarBeltTimerTable = $('#beltradar-belt-timer-table');
    /* Modals */
    const modalRequestDeleteSurvey = $('#beltradar-accept-delete-survey-session');
    const modalRequestDeleteBeltTimer = $('#beltradar-accept-delete-belt-timer');
    const modalRequestAddBeltTimer = $('#beltradar-add-belt-timer');

    /**
    * DataTable for Belt Radar Session Entries
    * Initialized empty and filled after async fetch.
    */
    const BeltRadarSessionsDataTable = new DataTable(BeltRadarSessionTable, {
        data: [],
        language: aaBeltRadarSettings.dataTables.language,
        layout: aaBeltRadarSettings.dataTables.layout,
        ordering: aaBeltRadarSettings.dataTables.ordering,
        columnControl: aaBeltRadarSettings.dataTables.columnControl,
        order: [[2, 'desc']],
        columnDefs: [
            {
                orderable: false,
                targets:  [3,4],
                columnControl: [
                    {target: 0, content: []},
                    {target: 1, content: []}
                ]
            },
        ],
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
                    display: (data) => data.name,
                    sort: (data) => data.name,
                    filter: (data) => data.name,
                }
            },
            {
                data: {
                    display: (data) => `${data.created_at}`,
                    sort: (data) => data.created_at,
                    filter: (data) => data.created_at,
                }
            },
            {
                data: {
                    display: (data) => data.owner,
                    sort: (data) => data.owner,
                    filter: (data) => data.owner,
                }
            },
            {
                data: {
                    display: (data) => data.html,
                    sort: (data) => data.created_at,
                    filter: (data) => data.created_at,
                }
            },
        ],
        initComplete: function() {
            _bootstrapTooltip({selector: '#beltradar-session-table'});
        },
        drawCallback: function () {
            _bootstrapTooltip({selector: '#beltradar-session-table'});
        },
    });

    /**
     * Fetch User Belt Sessions DataTable
     * Fetch the User Belt Sessions DataTable from the API Endpoint and populate the DataTable
     * If the fetch fails, log the error and clear the DataTable
     */
    fetchGetBeltRadar({
        url: aaBeltRadarSettings.url.mySessions,
    })
        .then((data) => {
            BeltRadarSessionsDataTable.clear().rows.add(data).draw();
        })
        .catch((error) => {
            console.error('Error fetching User Belt Sessions DataTable:', error);
            BeltRadarSessionsDataTable.clear().draw();
        });

    /**
    * Table :: Reload My Sessions DataTable
    * On Confirmation send a request to the API Endpoint, reload the Survey Sessions DataTable, close the modal
    * @param {string} url - The API Endpoint URL to send the delete request to returns {Promise}
    * @returns {Promise} - A Promise that resolves when the API request is complete
    */
    const _reloadSurveySessionsDataTable = (tableData) => {
        const dt = BeltRadarSessionTable.DataTable();
        dt.clear().rows.add(tableData).draw();
        BeltRadarSessionTable.addClass('highlight');

        setTimeout(() => {
            BeltRadarSessionTable.removeClass('highlight');
        }, 2000);
    };

    /**
    * Table :: Survey Sessions :: Delete Button Click Handler
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
            fetchPostBeltRadar({
                url: url,
                csrfToken: csrfMiddlewareToken,
                payload: {}
            })
                .then((data) => {
                    if (data.success === true) {
                        fetchGetBeltRadar({
                            url: aaBeltRadarSettings.url.mySessions,
                        })
                            .then((newData) => {
                                _reloadSurveySessionsDataTable(newData);
                                modalRequestDeleteSurvey.modal('hide');
                            })
                            .catch((error) => {
                                console.error('Error fetching Survey Sessions DataTable:', error);
                            });
                    }
                })
                .catch((error) => {
                    console.error(`Error posting delete request: ${error.message}`);
                });
        });
    })
        .on('hide.bs.modal', () => {
            modalRequestDeleteSurvey.find('#modal-button-confirm-accept-request').unbind('click');
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
                    display: (data) => data.eta_natural ? data.eta_natural : data.eta,
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

    /**
     * Fetch User Belt Timer DataTable
     * Fetch the User Belt Timer DataTable from the API Endpoint and populate the DataTable
     * If the fetch fails, log the error and clear the DataTable
     */
    fetchGetBeltRadar({
        url: aaBeltRadarSettings.url.myTimers,
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
        const beltPublicBool = form.find('input[name="public"]');

        beltTypeSelect.off('change.brBeltTimer').on('change.brBeltTimer', () => updateBeltSizeChoices({beltTypeSelect: beltTypeSelect.get(0), beltSizeSelect: beltSizeSelect.get(0)}));
        updateBeltSizeChoices({beltTypeSelect: beltTypeSelect.get(0), beltSizeSelect: beltSizeSelect.get(0)});

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
                    public: beltPublicBool.is(':checked'),
                }
            })
                .then((data) => {
                    if (data.success === true) {
                        fetchGetBeltRadar({
                            url: aaBeltRadarSettings.url.myTimers,
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
                        fetchGetBeltRadar({
                            url: aaBeltRadarSettings.url.myTimers,
                        })
                            .then((newData) => {
                                _reloadSurveyBeltTimerData(newData);
                                modalRequestDeleteBeltTimer.modal('hide');
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
            modalRequestDeleteBeltTimer.find('#modal-button-confirm-accept-request').unbind('click');
        });

});
