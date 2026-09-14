import { useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import Cookies from 'js-cookie';

import ApproveModal from '@/Components/Modals/BaseModal';

export interface BeltRadarModalsProps {
	session: any;
	modalAction: 'approve' | 'delete' | null;
	setModalAction: (action: 'approve' | 'delete' | null) => void;
	t: (key: string) => string;
}

function BeltRadarModals({ session, modalAction, setModalAction, t }: BeltRadarModalsProps) {
	const queryClient = useQueryClient();

	const onApprove = async (url: string) => {
		try {
			const response = await axios.post(url, {}, {
				withCredentials: true,
				headers: {
					'X-CSRFToken': Cookies.get('csrftoken') ?? '',
				},
			});

			if (response.data.success === true) {
				await queryClient.invalidateQueries({ queryKey: ['sessions'] });
			}
		} catch (error) {
			console.error(`Error posting session request: ${error}`);
		}
	};

    // boolean from session is_public and switch from actual value
    const isPublic = session?.is_public ?? false;

	return (
		<>
			<ApproveModal
				ApproveData={{
					title: t("Modify Session"),
					textBody: t("Are you sure you want to modify this session?"),
					buttonText: t("Modify"),
					url: `/beltradar/api/manage/session/${session.public_id}/modify/is_public/value/${isPublic ? 0 : 1}/`,
				}}
					showModal={modalAction === 'approve'}
					onApprove={onApprove}
				setShowModal={(show) => setModalAction(show ? 'approve' : null)}
			/>
			<ApproveModal
				ApproveData={{
					title: t("Delete Session"),
					textBody: t("Are you sure you want to delete this session?"),
					buttonText: t("Delete"),
					url: `/beltradar/api/manage/session/${session.public_id}/delete/`,
				}}
				showModal={modalAction === 'delete'}
				onApprove={onApprove}
				setShowModal={(show) => setModalAction(show ? 'delete' : null)}
			/>
		</>
	)
}

export default BeltRadarModals
