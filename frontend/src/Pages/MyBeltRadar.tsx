// Third Party
import { useTranslation } from 'react-i18next'

// AA Belt Radar
import CreateBeltTimerForm from '@/Components/Forms/CreateBeltTimerForm';
import CreateSessionForm from '@/Components/Forms/CreateSessionForm';
import { validateBeltTimerForm, validateSessionForm } from '@/Components/Forms/validation';
import ActionSectionHeader from '@/Components/Section/ActionSectionHeader';
import MyBeltRadarTable from '@/Components/Tables/MyBeltRadarTable';
import MyBeltTimerTable from '@/Components/Tables/MyBeltTimerTable';

function MyBeltRadar() {
	const { t } = useTranslation();

	return (
		<main className="br-page">
            {/* Sessions Section */}
			<ActionSectionHeader
				name={t("My Sessions")}
				modalKey="create_session"
				buttonTitle={t("Create Session")}
				validate={validateSessionForm}
				children={CreateSessionForm}
			/>
			<section aria-label={t("My Sessions")}>
				<MyBeltRadarTable />
			</section>

            {/* Belt Timers Section */}
			<ActionSectionHeader
				name={t("My Belt Timers")}
				modalKey="create_belt_timer"
				buttonTitle={t("Create Belt Timer")}
				validate={validateBeltTimerForm}
				children={CreateBeltTimerForm}
			/>
			<section aria-label={t("My Belt Timers")}>
				<MyBeltTimerTable />
			</section>

		</main>
	)
}

export default MyBeltRadar
