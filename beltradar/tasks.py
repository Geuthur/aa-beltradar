"""App Tasks"""

# Third Party
from celery import Task, shared_task

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger
from allianceauth.services.tasks import QueueOnce

# AA Belt Radar
from beltradar import __title__, app_settings
from beltradar.models import BeltSurveySession, EveMarketPrice
from beltradar.providers import AppLogger, retry_task_on_esi_error

logger = AppLogger(get_extension_logger(__name__), __title__)

MAX_RETRIES_DEFAULT = 3

# Default params for all tasks.
TASK_DEFAULTS = {
    "time_limit": app_settings.BELT_RADAR_TASK_TIME_LIMIT,
    "max_retries": MAX_RETRIES_DEFAULT,
}

# Default params for tasks that need bind=True.
TASK_DEFAULTS_BIND = {**TASK_DEFAULTS, **{"bind": True}}

# Default params for tasks that need bind=True and run once only.
TASK_DEFAULTS_BIND_ONCE = {**TASK_DEFAULTS, **{"bind": True, "base": QueueOnce}}

# Default params for tasks that need run once only.
TASK_DEFAULTS_ONCE = {**TASK_DEFAULTS, **{"base": QueueOnce}}

TASK_DEFAULTS_BIND_ONCE_SESSION = {
    **TASK_DEFAULTS_BIND_ONCE,
    **{"once": {"keys": ["public_id"], "graceful": True}},
}


@shared_task(**TASK_DEFAULTS_ONCE)
def update_all_belt_radar(runs: int = 0, force_refresh: bool = False):
    """Update all belt radar data."""
    sessions = BeltSurveySession.objects.all()
    for session in sessions:
        update_belt_radar_session.apply_async(
            kwargs={"public_id": session.public_id, "force_refresh": force_refresh}
        )
        runs = runs + 1
    logger.info("Queued %s Session Tasks", runs)


# pylint: disable=unused-argument
@shared_task(**TASK_DEFAULTS_BIND_ONCE_SESSION)
def update_belt_radar_session(self, public_id: str, force_refresh: bool = False):
    """Update a single belt radar session."""
    # Placeholder for future implementation, currently no background processing needed for session updates.


@shared_task(**TASK_DEFAULTS_BIND_ONCE)
def update_market_prices(self: Task):
    """Update market prices for all market items."""
    # Perform the update within the retry context manager
    with retry_task_on_esi_error(self):
        count = EveMarketPrice.objects.update_from_esi()
        logger.info("Updated market prices for %s items.", count)
