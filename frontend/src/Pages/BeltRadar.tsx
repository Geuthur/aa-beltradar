// Third Party
import { useTranslation } from 'react-i18next'

// AA Belt Radar
import BeltRadarTable from '@/Components/Tables/BeltRadarTable'
import BeltTimerTable from '@/Components/Tables/BeltTimerTable'
import CreateSessionForm from '@/Components/Forms/CreateSessionForm';
import { validateSessionForm } from '@/Components/Forms/validation';
import { ActionSectionHeader } from '@/Components/Section/ActionSectionHeader';

function BeltRadar() {
	const { t } = useTranslation();
	return (
		<main>
            {/* Sessions Section */}
			<ActionSectionHeader
				name={t("Sessions")}
				modalKey="create_session"
				buttonTitle={t("Create Session")}
				validate={validateSessionForm}
				children={CreateSessionForm}
			/>
			<section className="card" aria-labelledby="my-belt-radar-heading">
				<div className="card-body">
					<BeltRadarTable />
				</div>
			</section>

            {/* Belt Timers Section */}
			<ActionSectionHeader
				name={t("Belt Timers")}
				modalKey="create_belt_timer"
				buttonTitle={t("Create Belt Timer")}
				validate={validateSessionForm}
				children={CreateSessionForm}
			/>
			<section className="card" aria-labelledby="timers-heading">
				<div className="card-body">
					<BeltTimerTable />
				</div>
			</section>
		</main>
	)
}

export default BeltRadar
