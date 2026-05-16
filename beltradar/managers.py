# Standard Library
from datetime import date as dt_date
from typing import TYPE_CHECKING

# Django
from django.db import models

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter
from allianceauth.services.hooks import get_extension_logger

# AA Belt Radar
from beltradar import __title__
from beltradar.providers import AppLogger

if TYPE_CHECKING:
    # AA Belt Radar
    from beltradar.models import BeltSurveyEntry as BeltSurveyEntryContext
    from beltradar.models import BeltSurveySession as BeltSurveyContext

logger = AppLogger(get_extension_logger(__name__), __title__)


class BeltRadarQuerySet(models.QuerySet["BeltSurveyContext"]):
    def visible_to(self, user):
        """Get all survey sessions visible to the user."""
        # superusers get all visible
        if user.is_superuser:
            logger.debug(
                "Returning all survey sessions for superuser %s.",
                user,
            )
            return self

        if user.has_perm("taxsystem.admin_access"):
            logger.debug("Returning all survey sessions for admin user %s.", user)
            return self

        try:
            char = user.profile.main_character
            assert char
            queries = [models.Q(eve_character__character_ownership__user=user)]

            logger.debug(
                "%s queries for user %s visible survey sessions.", len(queries), user
            )

            query = queries.pop()
            for q in queries:
                query |= q
            return self.filter(query)
        except AssertionError:
            logger.debug("User %s has no main character. Nothing visible.", user)
            return self.none()

    def manage_to(self, user):
        """Get all survey sessions that the user can manage."""
        # superusers get all visible
        if user.is_superuser:
            logger.debug(
                "Returning all survey sessions for superuser %s.",
                user,
            )
            return self

        if user.has_perm("taxsystem.admin_access"):
            logger.debug("Returning all survey sessions for admin user %s.", user)
            return self

        try:
            char = user.profile.main_character
            assert char
            query = models.Q(eve_character__character_ownership__user=user)
            logger.debug("Returning own survey sessions for User %s.", user)

            if query is None:
                return self.none()

            return self.filter(query)
        except AssertionError:
            logger.debug("User %s has no main character. Nothing visible.", user)
            return self.none()


class BeltRadarManager(models.Manager["BeltSurveyContext"]):
    def get_queryset(self) -> BeltRadarQuerySet:
        return BeltRadarQuerySet(self.model, using=self._db)

    def visible_to(self, user):
        return self.get_queryset().visible_to(user)

    def manage_to(self, user):
        return self.get_queryset().manage_to(user)

    @staticmethod
    def visible_eve_characters(user):
        qs = EveCharacter.objects.get_queryset()
        if user.is_superuser:
            logger.debug("Returning all characters for superuser %s.", user)
            return qs.all()

        if user.has_perm("beltradar.admin_access"):
            logger.debug("Returning all characters for %s.", user)
            return qs.all()

        try:
            char = user.profile.main_character
            assert char
            queries = [models.Q(character_ownership__user=user)]

            logger.debug(
                "%s queries for user %s visible chracters.", len(queries), user
            )

            query = queries.pop()
            for q in queries:
                query |= q
            return qs.filter(query)
        except AssertionError:
            logger.debug("User %s has no main character. Nothing visible.", user)
            return qs.none()


class BeltSurveyEntryQuerySet(models.QuerySet["BeltSurveyEntryContext"]):
    def grouped_by_time(
        self, date: dt_date | None = None, tolerance_seconds: int = 60
    ) -> list[list["BeltSurveyEntryContext"]]:
        """Group entries by timestamp proximity.

        Entries are ordered by timestamp and grouped when they are within
        `tolerance_seconds` from the first entry of the current group.
        """
        qs = self.order_by("timestamp")
        if date is not None:
            qs = qs.filter(timestamp__date=date)

        entries = list(qs)
        if not entries:
            return []

        groups: list[list["BeltSurveyEntryContext"]] = []
        current_group = [entries[0]]
        group_start = entries[0].timestamp

        for entry in entries[1:]:
            if (entry.timestamp - group_start).total_seconds() <= tolerance_seconds:
                current_group.append(entry)
                continue

            groups.append(current_group)
            current_group = [entry]
            group_start = entry.timestamp

        groups.append(current_group)
        return groups


class BeltSurveyEntryManager(models.Manager["BeltSurveyEntryContext"]):
    def get_queryset(self) -> BeltSurveyEntryQuerySet:
        return BeltSurveyEntryQuerySet(self.model, using=self._db)

    def grouped_by_time(
        self, date: dt_date | None = None, tolerance_seconds: int = 60
    ) -> list[list["BeltSurveyEntryContext"]]:
        return self.get_queryset().grouped_by_time(
            date=date,
            tolerance_seconds=tolerance_seconds,
        )
