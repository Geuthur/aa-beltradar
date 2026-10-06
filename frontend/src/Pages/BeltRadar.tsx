// Third Party
import { useTranslation } from 'react-i18next'

// AA Belt Radar
import { ActionSectionHeader } from '@/Components/Base/ActionSectionHeader';
import CreateBeltTimerForm from '@/Components/Forms/CreateBeltTimerForm';
import CreateSessionForm from '@/Components/Forms/CreateSessionForm';
import { validateBeltTimerForm, validateSessionForm } from '@/Components/Forms/validation';
import BeltRadarTable from '@/Components/Tables/BeltRadarTable';
import BeltTimerTable from '@/Components/Tables/BeltTimerTable';

function BeltRadar() {
	const { t } = useTranslation();
	return (
		<main className="br-page">
            {/* Sessions Section */}
			<ActionSectionHeader
				name={t("Sessions")}
				modalKey="create_session"
				buttonTitle={t("Create Session")}
				validate={validateSessionForm}
				children={CreateSessionForm}
			/>
			<section aria-label={t("Sessions")}>
				<BeltRadarTable />
			</section>

            {/* Belt Timers Section */}
			<ActionSectionHeader
				name={t("Belt Timers")}
				modalKey="create_belt_timer"
				buttonTitle={t("Create Belt Timer")}
				validate={validateBeltTimerForm}
				children={CreateBeltTimerForm}
			/>
			<section aria-label={t("Belt Timers")}>
				<BeltTimerTable />
			</section>
		</main>
	)
}

export default BeltRadar
