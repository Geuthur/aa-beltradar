// Third Party
import { useTranslation } from 'react-i18next'

// AA Belt Radar
import MyBeltRadarTable from '@/Components/Tables/MyBeltRadarTable';
import MyBeltTimerTable from '@/Components/Tables/MyBeltTimerTable';
import ActionSectionHeader from '@/Components/Section/ActionSectionHeader';
import { validateSessionForm } from '@/Components/Forms/validation';
import CreateSessionForm from '@/Components/Forms/CreateSessionForm';

function MyBeltRadar() {
	const { t } = useTranslation();

	return (
		<main>
            {/* Sessions Section */}
			<ActionSectionHeader
				name={t("My Sessions")}
				modalKey="create_session"
				buttonTitle={t("Create Session")}
				validate={validateSessionForm}
				children={CreateSessionForm}
			/>
			<section className="card" aria-labelledby="my-belt-radar-heading">
				<div className="card-body">
					<MyBeltRadarTable />
				</div>
			</section>

            {/* Belt Timers Section */}
			<ActionSectionHeader
				name={t("My Belt Timers")}
				modalKey="create_belt_timer"
				buttonTitle={t("Create Belt Timer")}
				validate={validateSessionForm}
				children={CreateSessionForm}
			/>
			<section className="card" aria-labelledby="timers-heading">
				<div className="card-body">
					<MyBeltTimerTable />
				</div>
			</section>

		</main>
	)
}

export default MyBeltRadar
