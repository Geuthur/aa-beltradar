// Third Party
import { useTranslation } from 'react-i18next'

// AA Belt Radar
import BaseSectionHeader from '@/Components/Section/BaseSectionHeader';
import BeltRadarHeader from '@/Components/Section/BeltRadarHeader';
import BeltTimerTable from '@/Components/Tables/BeltTimerTable';
import MyBeltRadarTable from '@/Components/Tables/MyBeltRadarTable'

function MyBeltRadar() {
	const { t } = useTranslation();

	return (
		<main>
            {/* Sessions Section */}
			<BeltRadarHeader name={t("My Sessions")} />
			<section className="card" aria-labelledby="my-belt-radar-heading">
				<div className="card-body">
					<MyBeltRadarTable />
				</div>
			</section>

            {/* Belt Timers Section */}
			<BaseSectionHeader name={t("My Belt Timers")} />
			<section className="card" aria-labelledby="timers-heading">
				<div className="card-body">
					<BeltTimerTable />
				</div>
			</section>
		</main>
	)
}

export default MyBeltRadar
