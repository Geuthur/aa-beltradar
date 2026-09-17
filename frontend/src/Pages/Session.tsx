// React
import { useState } from 'react';
import { useParams } from 'react-router-dom';

// Third Party
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import { loadSession } from '@/Api/BeltRadar';
import { queryKeys } from "@/Api/query";
import { IconButton } from '@/Components/Icons/Icons';
import ErrorLoader from '@/Components/Loader/ErrorLoader';
import BaseModal from '@/Components/Modals/BaseModal';
import { useApproveMutation } from '@/Components/Modals/BeltRadarQuery';
import BaseSectionHeader from '@/Components/Section/BaseSectionHeader';
import SessionDashboard from '@/Components/Session/Dashboard';
import SessionSnapshotTable from '@/Components/Session/SnapshotTable';
import { renderTooltip } from '@/Components/Tables/BaseTable/tableHelper';

function BeltRadarSession() {
    const { t } = useTranslation();
    const { publicID } = useParams();
    const [showDeleteTimerModal, setShowDeleteTimerModal] = useState(false);
    const [showCreateTimerModal, setShowCreateTimerModal] = useState(false);

    const sessionKey = queryKeys.Session(String(publicID));

    // Load Belt Radar Session Snapshot data
    const { data: sessionData, isError: isErrorSessions } = useQuery({
        queryKey: sessionKey,
        queryFn: () => loadSession(String(publicID)),
        refetchOnWindowFocus: false,
        enabled: !!publicID,
    });

    const approveMutation = useApproveMutation([sessionKey, queryKeys.beltTimer]);

    if (isErrorSessions) {
        return <ErrorLoader title={t("Error 400")} message={t("Error loading session data")} />;
    }

    const headerName = sessionData?.name ? `${t("Session")} - ${sessionData.name}` : t("Session");
    const hasTimer = Boolean(sessionData?.has_timer || sessionData?.actions?.delete);
    const deleteTimerAction = sessionData?.actions?.delete;
    const createTimerAction = sessionData?.actions?.create;

    const handleDeleteTimer = async (url: string) => {
        await approveMutation.mutateAsync(url);
        setShowDeleteTimerModal(false);
    };

    const handleCreateTimer = async (url: string) => {
        await approveMutation.mutateAsync(url);
        setShowCreateTimerModal(false);
    };

    return (
        <main>
            {/* Sessions Section */}
            <BaseSectionHeader name={headerName}>
                {hasTimer ? (
                    <div className="d-flex align-items-center gap-2">
                        {renderTooltip(
                            t("Belt Timer active"),
                            <span className="text-white d-inline-flex align-items-center" style={{ fontSize: "1.2rem" }}>
                                <i className="fa-solid fa-stopwatch"></i>
                            </span>
                        )}
                        {deleteTimerAction && (
                            <IconButton
                                icon={deleteTimerAction.icon ?? "fa-solid fa-trash"}
                                color={deleteTimerAction.color ?? "danger"}
                                title={deleteTimerAction.title ?? t("Delete Belt Timer")}
                                onClick={() => setShowDeleteTimerModal(true)}
                                classProps="me-0"
                            />
                        )}
                    </div>
                ) : (
                    createTimerAction && (
                        <IconButton
                            icon={createTimerAction.icon ?? "fa-solid fa-plus"}
                            color={createTimerAction.color ?? "success"}
                            title={createTimerAction.title ?? t("Create Belt Timer")}
                            onClick={() => setShowCreateTimerModal(true)}
                            classProps="me-0"
                        />
                    )
                )}
            </BaseSectionHeader>
            {/* Session Dashboard */}
            <SessionDashboard sessionData={sessionData} />
            {/* Session Snapshot Table */}
            <SessionSnapshotTable />

            {/* Belt Timer Modals */}
            {deleteTimerAction && (
                <BaseModal
                    data={deleteTimerAction}
                    showModal={showDeleteTimerModal}
                    setShowModal={setShowDeleteTimerModal}
                    onApprove={({ url }) => handleDeleteTimer(url)}
                    isPending={approveMutation.isPending}
                    children={<div>{deleteTimerAction.text}</div>}
                />
            )}
            {createTimerAction && (
                <BaseModal
                    data={createTimerAction}
                    showModal={showCreateTimerModal}
                    setShowModal={setShowCreateTimerModal}
                    onApprove={({ url }) => handleCreateTimer(url)}
                    isPending={approveMutation.isPending}
                    children={<div>{createTimerAction.text}</div>}
                />
            )}
        </main>
    );
}

export default BeltRadarSession;
