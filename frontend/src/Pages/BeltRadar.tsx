// Third Party
import { useTranslation } from 'react-i18next'

// AA Belt Radar
import BaseSectionHeader from '@/Components/Section/BaseSectionHeader';
import BeltRadarHeader from '@/Components/Section/BeltRadarHeader';
import BeltRadarTable from '@/Components/Tables/BeltRadarTable'
import BeltTimerTable from '@/Components/Tables/BeltTimerTable'

function BeltRadar() {
	const { t } = useTranslation();
	return (
		<main>
            {/* Sessions Section */}
			<BeltRadarHeader name={t("Sessions")} />
			<section className="card" aria-labelledby="my-belt-radar-heading">
				<div className="card-body">
					<BeltRadarTable />
				</div>
			</section>

            {/* Belt Timers Section */}
			<BaseSectionHeader name={t("Belt Timers")} />
			<section className="card" aria-labelledby="timers-heading">
				<div className="card-body">
					<BeltTimerTable />
				</div>
			</section>
		</main>
	)
}

export default BeltRadar
