"""App Tasks"""

# Standard Library
import inspect
from collections.abc import Callable

# Third Party
from celery import Task, chain, shared_task

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger
from allianceauth.services.tasks import QueueOnce

# AA Example
from example import __title__, app_settings
from example.models import Example
from example.models.helpers.update_manager import UpdateSection
from example.providers import AppLogger, retry_task_on_esi_error

logger = AppLogger(get_extension_logger(__name__), __title__)

MAX_RETRIES_DEFAULT = 3

# Default params for all tasks.
TASK_DEFAULTS = {
    "time_limit": app_settings.EXAMPLE_TASKS_TIME_LIMIT,
    "max_retries": MAX_RETRIES_DEFAULT,
}

# Default params for tasks that need bind=True.
TASK_DEFAULTS_BIND = {**TASK_DEFAULTS, **{"bind": True}}

# Default params for tasks that need bind=True and run once only.
TASK_DEFAULTS_BIND_ONCE = {**TASK_DEFAULTS, **{"bind": True, "base": QueueOnce}}

# Default params for tasks that need run once only.
TASK_DEFAULTS_ONCE = {**TASK_DEFAULTS, **{"base": QueueOnce}}

TASK_DEFAULTS_BIND_ONCE_OWNER = {
    **TASK_DEFAULTS_BIND_ONCE,
    **{"once": {"keys": ["eve_id"], "graceful": True}},
}


@shared_task(**TASK_DEFAULTS_ONCE)
def example_task(runs: int = 0, force_refresh: bool = False):
    characters = Example.objects.select_related("eve_character").all()
    for character in characters:
        update_example.apply_async(
            args=[character.eve_id], kwargs={"force_refresh": force_refresh}
        )
        runs = runs + 1
    logger.debug("Queued %s Example Tasks", runs)


# pylint: disable=unused-argument
@shared_task(**TASK_DEFAULTS_BIND_ONCE_OWNER)
def update_example(self: Task, eve_id: int, force_refresh=False) -> bool:
    """Update a owner

    Args:
        eve_id (int): Eve ID of the Owner to update
        force_refresh (bool): Whether to force a refresh of all sections

    Returns:
        True if the task was successful, False otherwise
    """
    character = Example.objects.get(eve_character__character_id=eve_id)

    if character.is_orphan:
        logger.info(
            "Character %s is an orphan. Skipping update.",
            character,
        )
        return False

    que = []
    priority = 7

    logger.debug(
        "Processing Example Updates for %s",
        format(character.eve_character.character_name),
    )

    if force_refresh:
        # Reset Token Error if we are forcing a refresh
        character.update_manager.reset_has_token_error()

    needs_update = character.update_manager.calc_update_needed()

    if not needs_update and not force_refresh:
        logger.info("No updates needed for %s", character.eve_character.character_name)
        return False

    sections = UpdateSection.get_sections()

    for section in sections:
        # Skip sections that are not in the needs_update list
        if not force_refresh and not needs_update.for_section(section):
            logger.debug(
                "No updates needed for %s (%s)",
                character.eve_character.character_name,
                section,
            )
            continue

        task_name = f"update_example_{section}"
        task = globals().get(task_name)
        que.append(
            task.si(character.eve_id, force_refresh=force_refresh).set(
                priority=priority
            )
        )

    chain(que).apply_async()
    logger.debug(
        "Queued %s Example Updates for %s",
        len(que),
        character.eve_character.character_name,
    )
    return True


@shared_task(**TASK_DEFAULTS_BIND_ONCE_OWNER)
def update_example_example(self: Task, eve_id: int, force_refresh: bool):
    logger.debug("Starting update_example task for eve_id: %s", eve_id)
    return _update_section(
        task=self,
        eve_id=eve_id,
        section=UpdateSection.EXAMPLE,
        force_refresh=force_refresh,
    )


def _update_section(task: Task, eve_id: int, section: str, force_refresh: bool):
    """Update a specific section."""
    logger.debug("Starting update for section %s, eve_id: %s", section, eve_id)
    section = UpdateSection(section)
    character = Example.objects.get(eve_character__character_id=eve_id)
    logger.debug(
        "Updating %s for %s", section.label, character.eve_character.character_name
    )

    character.update_manager.reset_update_status(section)

    method: Callable = getattr(character, section.method_name)
    method_signature = inspect.signature(method)

    if "force_refresh" in method_signature.parameters:
        kwargs = {"force_refresh": force_refresh}
    else:
        kwargs = {}

    with retry_task_on_esi_error(task):
        result = character.update_manager.perform_update_status(
            section, method, **kwargs
        )
    character.update_manager.update_section_log(section, result)
