// Third Party
import { useTranslation } from 'react-i18next'

// AA Belt Radar
import BeltTimerTable from '@/Components/Tables/BeltTimerTable';
import MyBeltRadarTable from '@/Components/Tables/MyBeltRadarTable'

function MyBeltRadar() {
	const { t } = useTranslation();

	return (
		<main>
            {/* Sessions Section */}
            <section className="card" aria-labelledby="sessions-heading">
				<div className="card-header bg-primary">
					<h2 id="sessions-heading">{t("Sessions")}</h2>
				</div>
				<div className="card-body">
					<MyBeltRadarTable />
				</div>
			</section>

            {/* Belt Timers Section */}
			<section className="card mt-5" aria-labelledby="timers-heading">
				<div className="card-header bg-primary">
					<h2 id="timers-heading">{t("My Belt Timers")}</h2>
				</div>
				<div className="card-body">
					<BeltTimerTable />
				</div>
			</section>
		</main>
	)
}

export default MyBeltRadar
