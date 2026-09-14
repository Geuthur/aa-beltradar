// Third Party
import { useTranslation } from 'react-i18next'

function Settings() {
	const { t } = useTranslation();

	return (
		<main>
            {/* Sessions Section */}
            <section className="card" aria-labelledby="settings-heading">
				<div className="card-header bg-primary">
					<h2 id="settings-heading">{t("User Settings")}</h2>
				</div>
				<div className="card-body">
				</div>
			</section>
		</main>
	)
}

export default Settings
