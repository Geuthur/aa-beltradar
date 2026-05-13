# Standard Library
from typing import TYPE_CHECKING

# Django
from django.db import models

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# AA Example
from example import __title__
from example.decorators import log_timing
from example.models.helpers.update_manager import UpdateSection, UpdateSectionResult
from example.providers import AppLogger

if TYPE_CHECKING:
    # AA Example
    from example.models import Example as ExampleContext

logger = AppLogger(get_extension_logger(__name__), __title__)


class ExampleQuerySet(models.QuerySet["ExampleContext"]):
    pass


class ExampleManager(models.Manager["ExampleContext"]):
    def get_queryset(self) -> ExampleQuerySet:
        return ExampleQuerySet(self.model, using=self._db)

    @log_timing(logger)
    def update_or_create_esi(
        self, owner: "ExampleContext", force_refresh: bool = False
    ) -> "UpdateSectionResult":
        """Update or Create a wallet journal entry from ESI data."""
        return owner.update_manager.update_section_if_changed(
            section=UpdateSection.EXAMPLE,
            fetch_func=self._fetch_example,
            force_refresh=force_refresh,
        )

    def _fetch_example(self, owner: "ExampleContext", force_refresh: bool) -> None:
        """
        Fetch the Example data from ESI and update the owner instance.
        """
