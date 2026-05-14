# Standard Library
from typing import TYPE_CHECKING

# Django
from django.db import models

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# AA Belt Radar
from beltradar import __title__
from beltradar.models.helpers.update_manager import UpdateSection, UpdateSectionResult
from beltradar.providers import AppLogger

if TYPE_CHECKING:
    # AA Belt Radar
    from beltradar.models import BeltRadar as BeltRadarContext

logger = AppLogger(get_extension_logger(__name__), __title__)


class BeltRadarQuerySet(models.QuerySet["BeltRadarContext"]):
    pass


class OwnerManager(models.Manager["BeltRadarContext"]):
    def get_queryset(self) -> BeltRadarQuerySet:
        return BeltRadarQuerySet(self.model, using=self._db)

    def update_or_create_esi(
        self, owner: "BeltRadarContext", force_refresh: bool = False
    ) -> "UpdateSectionResult":
        """Update or Create a wallet journal entry from ESI data."""
        return owner.update_manager.update_section_if_changed(
            section=UpdateSection.BELT_RADAR,
            fetch_func=self._fetch_beltradar,
            force_refresh=force_refresh,
        )

    def _fetch_beltradar(self, owner: "BeltRadarContext", force_refresh: bool) -> None:
        """
        Fetch the Belt Radar data from ESI and update the owner instance.
        """
