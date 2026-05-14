"""Models for Belt Radar."""

# Django
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter
from allianceauth.services.hooks import get_extension_logger

# AA Belt Radar
from beltradar import __title__, app_settings
from beltradar.managers import OwnerManager
from beltradar.models.helpers.update_manager import (
    UpdateManager,
    UpdateSection,
    UpdateSectionResult,
)
from beltradar.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)

class Owner(models.Model):
    """Belt Radar model for app"""

    class Meta:
        default_permissions = ()  # Remove standard permissions

    objects: OwnerManager = OwnerManager()

    name = models.CharField(max_length=100, null=True, default=None)

    eve_character = models.OneToOneField(
        EveCharacter, on_delete=models.CASCADE, related_name="belt_radar_character"
    )

    def __str__(self) -> str:
        try:
            return f"{self.eve_character.character_name} ({self.pk})"
        except AttributeError:
            return f"{self.name} ({self.pk})"

    @property
    def eve_id(self) -> int:
        """Return the Eve ID of this character."""
        return self.eve_character.character_id

    @property
    def update_manager(self):
        """Return the Update Manager helper for this owner."""
        return UpdateManager(
            owner=self,
            update_section=UpdateSection,
            update_status=UpdateStatus,
        )

    @cached_property
    def character_ownership(self) -> bool:
        """
        Return the character ownership object of this character.
        """
        try:
            return self.eve_character.character_ownership
        except ObjectDoesNotExist:
            return None

    @cached_property
    def is_orphan(self) -> bool:
        """
        Return True if this character is an orphan else False.

        An orphan is a character that is not owned anymore by a user.
        """
        return self.character_ownership is None

    def update_belt_radar(self, force_refresh: bool) -> UpdateSectionResult:
        return self.objects.update_or_create_esi(self, force_refresh=force_refresh)


class UpdateStatus(models.Model):
    """A Model to track the status of the last update."""

    class Meta:
        default_permissions = ()

    owner = models.ForeignKey(
        Owner, on_delete=models.CASCADE, related_name="belt_radar_update_status"
    )
    section = models.CharField(
        max_length=32, choices=UpdateSection.choices, db_index=True
    )
    is_success = models.BooleanField(default=None, null=True, db_index=True)
    error_message = models.TextField()
    has_token_error = models.BooleanField(default=False)

    last_run_at = models.DateTimeField(
        default=None,
        null=True,
        db_index=True,
        help_text="Last run has been started at this time",
    )
    last_run_finished_at = models.DateTimeField(
        default=None,
        null=True,
        db_index=True,
        help_text="Last run has been successful finished at this time",
    )
    last_update_at = models.DateTimeField(
        default=None,
        null=True,
        db_index=True,
        help_text="Last update has been started at this time",
    )
    last_update_finished_at = models.DateTimeField(
        default=None,
        null=True,
        db_index=True,
        help_text="Last update has been successful finished at this time",
    )

    def __str__(self) -> str:
        return f"{self.owner} - {self.section}"

    def need_update(self) -> bool:
        """Check if the update is needed."""
        if not self.is_success or not self.last_update_finished_at:
            needs_update = True
        else:
            section_time_stale = app_settings.BELT_RADAR_STALE_TYPES.get(self.section, 60)
            stale = timezone.now() - timezone.timedelta(minutes=section_time_stale)

            try:
                needs_update = self.last_update_finished_at <= stale
            except AttributeError:
                logger.debug("Last update finished at is None, needs update")
                needs_update = True

        if needs_update and self.has_token_error:
            logger.info(
                "%s: Ignoring update because of token error, section: %s",
                self,
                self.section,
            )
            needs_update = False

        return needs_update

    def reset(self) -> None:
        """Reset this update status."""
        self.is_success = None
        self.error_message = ""
        self.has_token_error = False
        self.last_run_at = timezone.now()
        self.last_run_finished_at = None
        self.save()
