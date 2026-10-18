// Third Party
import { Card } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import ActionSectionHeader from '@/Components/Base/ActionSectionHeader';
import CreateBeltTimerForm from '@/Components/Forms/CreateBeltTimerForm';
import CreateSessionForm from '@/Components/Forms/CreateSessionForm';
import { validateBeltTimerForm, validateSessionForm } from '@/Components/Forms/validation';
import MyBeltRadarTable from '@/Components/Tables/MyBeltRadarTable';
import MyBeltTimerTable from '@/Components/Tables/MyBeltTimerTable';

function MyBeltRadar() {
	const { t } = useTranslation();

	return (
		<div className="br-page">
			{/* Sessions Section */}
			<ActionSectionHeader
				name={t("My Sessions")}
				modalKey="create_session"
				buttonTitle={t("Create Session")}
				validate={validateSessionForm}
				children={CreateSessionForm}
			/>
			<Card.Body className="text-light border-0 shadow-sm p-0" aria-label={t("My Sessions")}>
				<MyBeltRadarTable />
			</Card.Body>

			{/* Belt Timers Section */}
			<ActionSectionHeader
				name={t("My Belt Timers")}
				modalKey="create_belt_timer"
				buttonTitle={t("Create Belt Timer")}
				validate={validateBeltTimerForm}
				children={CreateBeltTimerForm}
			/>
			<Card.Body className="text-light border-0 shadow-sm p-0" aria-label={t("My Belt Timers")}>
				<MyBeltTimerTable />
			</Card.Body>
		</div>
	);
}

export default MyBeltRadar;
