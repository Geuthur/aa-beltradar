"""App Tasks"""

# Standard Library
from urllib.parse import urljoin

# Third Party
from celery import Task, shared_task

# Django
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger
from allianceauth.services.tasks import QueueOnce

# AA Belt Radar
from beltradar import __title__, app_settings
from beltradar.models import BeltSurveySession, BeltTimer, EveMarketPrice, UserSettings
from beltradar.providers import AppLogger, retry_task_on_esi_error
from beltradar.thirdparty.discord import send_user_notification

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
def update_all_belt_radar(runs: int = 0):
    """Update all belt radar data."""
    sessions = BeltSurveySession.objects.all()
    user_notifications = {}
    updated_timers = []
    now = timezone.now()

    for session in sessions:
        # Get or create user settings for the session owner
        user_settings = UserSettings.objects.get_or_create(user=session.owner)[0]

        # Create a list of notifications for the user if the session has any timers that have expired
        if not user_notifications.get(user_settings.user.pk):
            user_notifications[user_settings.user.pk] = []

        # Check if any timers have expired and add a notification message for the user
        for timer in session.br_timer.all():
            # Check if the timer has expired and if a notification has not been sent yet
            if timer.eta and timer.eta < now and timer.sent_notification is False:
                logger.debug(
                    "Timer for belt %s has expired. trying to send notification.",
                    timer.session,
                )

                # Create a notification message for the user with a link to the session
                url = urljoin(
                    settings.SITE_URL,
                    reverse(
                        "beltradar:view_session",
                        args=[session.public_id],
                    ),
                )
                msg = _("Belt ID: **{belt_id}** - [Session]({url})").format(
                    belt_id=timer.belt_id,
                    url=url,
                )

                # Add the notification message to the user's list of notifications if notifications are not disabled
                if not user_settings.disable_notifications:
                    user_notifications[user_settings.user.pk].append(msg)

                # Mark the timer as having sent a notification to avoid sending duplicate notifications
                timer.sent_notification = True
                # Add the timer to the list of updated timers to be saved later
                updated_timers.append(timer)
        # Increment the run counter
        runs = runs + 1

    # Save all updated timers in bulk to reduce database hits
    if updated_timers:
        logger.debug("Updating %s expired timers.", len(updated_timers))
        BeltTimer.objects.bulk_update(updated_timers, ["sent_notification"])

    # Send notifications to users if there are any messages to send
    for user_id, messages in user_notifications.items():
        if messages:
            logger.debug(
                "Sending notification to user %s for %s expired timers.",
                user_id,
                len(messages),
            )
            title = _("Belt Radar Notification")
            message = "\n".join(messages)
            message += _("\n\nhas respawned.")
            send_user_notification.delay(
                user_id=user_id,
                title=title,
                message=message,
                embed_message=True,
                level="info",
            )
    logger.info("Queued %s Session Tasks", runs)


@shared_task(**TASK_DEFAULTS_BIND_ONCE)
def update_market_prices(self: Task):
    """Update market prices for all market items."""
    # Perform the update within the retry context manager
    with retry_task_on_esi_error(self):
        count = EveMarketPrice.objects.update_from_esi()
        logger.info("Updated market prices for %s items.", count)
