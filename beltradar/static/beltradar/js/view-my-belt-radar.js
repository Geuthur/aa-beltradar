/* global aaBeltRadarSettings, aaBeltRadarSettingsOverride, aaBeltRadarBeltTimerLayout, _bootstrapTooltip, DataTable, numberFormatter, moment, ApexCharts, updateBeltSizeChoices, fetchGetBeltRadar, fetchPostBeltRadar */

$(document).ready(() => {
    /* Initialize Bootstrap Tooltips */
    _bootstrapTooltip();
    /* DataTable for Belt Radar Session Entries */
    const BeltRadarSessionTable = $('#beltradar-session-table');
    const BeltRadarBeltTimerTable = $('#beltradar-belt-timer-table');
    /* Modals */
    const modalRequestAddBeltTimer = $('#beltradar-add-belt-timer');
    const modalRequestModifyBeltTimer = $('#beltradar-accept-modify-belt-timer');
    const modalRequestDeleteBeltTimer = $('#beltradar-accept-delete-belt-timer');
    const modalRequestAddSession = $('#beltradar-add-session');
    const modalRequestModifySession = $('#beltradar-accept-modify-session');
    const modalRequestDeleteSession = $('#beltradar-accept-delete-session');

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
                targets:  [3,4,5],
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
                    display: (data) => data.public.display,
                    sort: (data) => data.public.sort,
                    filter: (data) => data.public.raw,
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
    * On Confirmation send a request to the API Endpoint, reload the Session DataTable, close the modal
    * @param {string} url - The API Endpoint URL to send the delete request to returns {Promise}
    * @returns {Promise} - A Promise that resolves when the API request is complete
    */
    const _reloadSessionsDataTable = (tableData) => {
        const dt = BeltRadarSessionTable.DataTable();
        dt.clear().rows.add(tableData).draw();
        BeltRadarSessionTable.addClass('highlight');

        setTimeout(() => {
            BeltRadarSessionTable.removeClass('highlight');
        }, 2000);
    };

    /**
    * Table :: Session :: Delete Button Click Handler
    * Open Delete Session Modal
    * On Confirmation send a request to the API Endpoint, reload the Session DataTable, close the modal
    * and reopen the previous Session Modal
    */
    modalRequestDeleteSession.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('action');
        const form = modalRequestDeleteSession.find('form');
        const csrfMiddlewareToken = form.find('input[name="csrfmiddlewaretoken"]').val();

        modalRequestDeleteSession.find('#modal-button-confirm-accept-request').on('click', () => {
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
                                _reloadSessionsDataTable(newData);
                                modalRequestDeleteSession.modal('hide');
                            })
                            .catch((error) => {
                                console.error('Error fetching Session DataTable:', error);
                            });
                    }
                })
                .catch((error) => {
                    console.error(`Error posting delete request: ${error.message}`);
                });
        });
    })
        .on('hide.bs.modal', () => {
            modalRequestDeleteSession.find('#modal-button-confirm-accept-request').unbind('click');
        });

    /**
    * DataTable for Belt Radar Session - Belt Timer
    * Initialized empty and filled after async fetch.
    */
    const BeltRadarBeltTimerDataTable = new DataTable(BeltRadarBeltTimerTable, {
        data: [],
        language: aaBeltRadarSettings.dataTables.language,
        layout: aaBeltRadarBeltTimerLayout,
        ordering: aaBeltRadarSettings.dataTables.ordering,
        columnControl: aaBeltRadarSettings.dataTables.columnControl,
        // Sort by ETA (column index 5) so the next expiring timer is always first.
        order: [[5, 'asc'], [0, 'asc']],
        columnDefs: [
            {
                orderable: false,
                targets:  [6,7],
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
                    display: (data) => data.eta.display,
                    sort: (data) => data.is_expired ? '9999-12-31 23:59:59.999999+00:00' : data.eta.sort,
                    filter: (data) => data.eta.raw,
                }
            },
            {
                data: {
                    display: (data) => data.public.display,
                    sort: (data) => data.public.sort,
                    filter: (data) => data.public.raw,
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

            const dt = BeltRadarBeltTimerTable.DataTable();

            /**
             * Helper function: Filter DataTable using DataTables custom search API
             */
            const applyPaymentFilter = (predicate) => {
                // reset custom filters and add a table-scoped predicate
                $.fn.dataTable.ext.search = [];
                $.fn.dataTable.ext.search.push(function(settings, searchData, index, rowData) {
                    // only apply to this DataTable instance
                    try {
                        if (settings.nTable !== dt.table().node()) {
                            return true;
                        }
                    } catch (e) {
                        console.log('error catch');
                        return true;
                    }

                    if (!rowData) return true;
                    return predicate(rowData);
                });
                dt.draw();
            };

            let dateFilter = new Date(Date.now() - ( 3600 * 1000 * 24 * 7));
            applyPaymentFilter(rowData => !(new Date(rowData.eta.raw) <= dateFilter));

            $('.request-filter-all').on('change click', () => {
                applyPaymentFilter(() => true);
            });
        },
        drawCallback: function () {
            _bootstrapTooltip({selector: '#beltradar-belt-timer-table'});
        },
        rowCallback: function(row, data) {
            if (data.is_expired) {
                $(row).addClass('text-muted text-decoration-line-through opacity-50');
            }
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
    const _reloadBeltTimerData = (tableData) => {
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
        const beltPublicBool = form.find('input[name="is_public"]');

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
                    is_public: beltPublicBool.is(':checked'),
                }
            })
                .then((data) => {
                    if (data.success === true) {
                        fetchGetBeltRadar({
                            url: aaBeltRadarSettings.url.myTimers,
                        })
                            .then((freshData) => {
                                _reloadBeltTimerData(freshData);
                                modalRequestAddBeltTimer.modal('hide');
                            })
                            .catch((error) => {
                                console.error('Error fetching Belt Timer DataTable after add:', error);
                                modalRequestAddBeltTimer.find('#beltradar-error').text(error.message).removeClass('d-none').addClass('br-shake');
                            });
                    }
                })
                .catch((error) => {
                    console.error(`Error posting add belt timer request: ${error.message}`);
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
            modalRequestAddBeltTimer.find('input[name="is_public"]').prop('checked', false);
            modalRequestAddBeltTimer.find('#beltradar-spinner').addClass('d-none');
            modalRequestAddBeltTimer.find('#beltradar-error').addClass('d-none').removeClass('br-shake').text('');
        });

    /**
    * Table :: Belt-Timer :: Delete Button Click Handler
    * Open Delete Belt-Timer Modal
    * On Confirmation send a request to the API Endpoint, reload the Belt-Timer DataTable, close the modal
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
                                _reloadBeltTimerData(newData);
                                modalRequestDeleteBeltTimer.modal('hide');
                            })
                            .catch((error) => {
                                console.error('Error fetching Belt Timer DataTable:', error);
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

    /**
    * Table :: Belt-Timer :: Modify Button Click Handler
    * Open Modify Belt-Timer Modal
    * On Confirmation send a request to the API Endpoint, reload the Belt-Timer DataTable, close the modal
    */
    modalRequestModifyBeltTimer.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('action');
        const form = modalRequestModifyBeltTimer.find('form');
        const csrfMiddlewareToken = form.find('input[name="csrfmiddlewaretoken"]').val();

        modalRequestModifyBeltTimer.find('#modal-button-confirm-accept-request').on('click', () => {
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
                                _reloadBeltTimerData(newData);
                                modalRequestModifyBeltTimer.modal('hide');
                            })
                            .catch((error) => {
                                console.error('Error fetching Belt Timer DataTable:', error);
                            });
                    }
                })
                .catch((error) => {
                    console.error(`Error posting modify request: ${error.message}`);
                });
        });
    })
        .on('hide.bs.modal', () => {
            modalRequestModifyBeltTimer.find('#modal-button-confirm-accept-request').unbind('click');
        });

    /**
    * View :: Session :: Add Session Button Click Handler
    * Open Add Session Modal
    * On Confirmation send a request to the API Endpoint, reload the Session DataTable, close the modal
    */
    modalRequestAddSession.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('action');
        const form = modalRequestAddSession.find('form');
        const nativeForm = form.get(0);
        const csrfMiddlewareToken = form.find('input[name="csrfmiddlewaretoken"]').val();
        const sessionNameInput = form.find('input[name="name"]');
        const sessionIsPublicCheckbox = form.find('input[name="is_public"]');

        modalRequestAddSession.find('#modal-button-confirm-add-request').on('click', () => {
            if (nativeForm && !nativeForm.checkValidity()) {
                nativeForm.reportValidity();
                return;
            }

            modalRequestAddSession.find('#beltradar-spinner').removeClass('d-none');
            modalRequestAddSession.find('#beltradar-error').addClass('d-none').removeClass('br-shake').text('');
            fetchPostBeltRadar({
                url: url,
                csrfToken: csrfMiddlewareToken,
                payload: {
                    name: sessionNameInput.val(),
                    is_public: sessionIsPublicCheckbox.is(':checked'),
                }
            })
                .then((data) => {
                    if (data.success === true) {
                        fetchGetBeltRadar({
                            url: aaBeltRadarSettings.url.mySessions,
                        })
                            .then((freshData) => {
                                _reloadSessionsDataTable(freshData);
                                modalRequestAddSession.modal('hide');
                            })
                            .catch((error) => {
                                console.error('Error fetching Session DataTable after add:', error);
                                modalRequestAddSession.find('#beltradar-error').text(error.message).removeClass('d-none').addClass('br-shake');
                            });
                    }
                })
                .catch((error) => {
                    console.error(`Error posting add session request: ${error.message}`);
                    modalRequestAddSession.find('#beltradar-error').text(error.message).removeClass('d-none').addClass('br-shake');
                })
                .finally(() => {
                    modalRequestAddSession.find('#beltradar-spinner').addClass('d-none');
                });
        });
    })
        .on('hide.bs.modal', () => {
            modalRequestAddSession.find('#modal-button-confirm-add-request').unbind('click');
            modalRequestAddSession.find('input[name="name"]').val('');
            modalRequestAddSession.find('input[name="is_public"]').prop('checked', true);
            modalRequestAddSession.find('#beltradar-spinner').addClass('d-none');
            modalRequestAddSession.find('#beltradar-error').addClass('d-none').removeClass('br-shake').text('');
        });

    /**
    * Table :: Session :: Modify Button Click Handler
    * Open Modify Session Modal
    * On Confirmation send a request to the API Endpoint, reload the Session DataTable, close the modal
    */
    modalRequestModifySession.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('action');
        const form = modalRequestModifySession.find('form');
        const csrfMiddlewareToken = form.find('input[name="csrfmiddlewaretoken"]').val();

        modalRequestModifySession.find('#modal-button-confirm-accept-request').on('click', () => {
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
                            .then((freshData) => {
                                _reloadSessionsDataTable(freshData);
                                modalRequestModifySession.modal('hide');
                            })
                            .catch((error) => {
                                console.error('Error fetching Session DataTable:', error);
                            });
                    }
                })
                .catch((error) => {
                    console.error(`Error posting modify request: ${error.message}`);
                });
        });
    })
        .on('hide.bs.modal', () => {
            modalRequestModifySession.find('#modal-button-confirm-accept-request').unbind('click');
        });
});
