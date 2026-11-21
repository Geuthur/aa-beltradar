"""Access control for the app: querysets and managers with `visible_to` and `manage_to`."""

# Standard Library
from typing import Generic, TypeVar

# Django
from django.db import models

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter

# AA Belt Radar
from beltradar.providers import logger

T = TypeVar("T", bound=models.Model)


class GeneralManager(models.Manager):
    """
    Manager of `General` for the app's own permission rules.

    The API, its helpers and the menu hook check permissions only through this
    manager. The Django views keep `@permission_required("beltradar.basic_access")`.
    `AccessQuerySet` and `AccessManager` ask it for the admin rule.
    `General` is not managed, so these methods never query `General`.
    """

    @staticmethod
    def has_basic_access(user) -> bool:
        """Users with `basic_access` may use the app."""
        return bool(user.has_perm("beltradar.basic_access"))

    @staticmethod
    def has_management_access(user) -> bool:
        """Users with `manage_access` or `admin_access` may manage."""
        return bool(
            user.has_perm("beltradar.manage_access")
            or user.has_perm("beltradar.admin_access")
        )

    @staticmethod
    def has_admin_access(user) -> bool:
        """Superusers and users with `admin_access` see and manage everything."""
        return bool(user.is_superuser or user.has_perm("beltradar.admin_access"))


class AccessQuerySet(models.QuerySet[T], Generic[T]):
    """
    A QuerySet with access control methods for the whole Application.

    The rules assume an `owner` foreign key to the user and an `is_public`
    flag: a user sees their own and all public objects and manages their own.
    Override `visible_q` and `manage_q` in a subclass when a model needs other rules.

    Methods:
        visible_to(user): Returns objects visible to the given user.
        manage_to(user): Returns objects the given user can manage.
    """

    def owned_by_q(self, user) -> models.Q:
        """Q object for the objects that belong to the user."""
        return models.Q(owner=user)

    def visible_q(self, user) -> models.Q:
        """Q object for the objects a user without admin access may see."""
        return self.owned_by_q(user) | models.Q(is_public=True)

    def manage_q(self, user) -> models.Q:
        """Q object for the objects a user without admin access may manage."""
        return self.owned_by_q(user)

    def _restricted_to(self, user, query: models.Q, what: str):
        if GeneralManager.has_admin_access(user):
            logger.debug("Returning all %s objects for %s.", what, user)
            return self

        if not getattr(user.profile, "main_character", None):
            logger.debug("User %s has no main character. Nothing %s.", user, what)
            return self.none()

        return self.filter(query)

    def visible_to(self, user):
        """Get all objects visible to the user."""
        return self._restricted_to(user, self.visible_q(user), "visible")

    def manage_to(self, user):
        """Get QuerySet of objects that the user can manage."""
        return self._restricted_to(user, self.manage_q(user), "manageable")


class AccessManager(models.Manager[T], Generic[T]):
    """
    A Manager with access control methods for the whole Application

    This manager provides methods to filter querysets based on user permissions,
    such as `visible_to` and `manage_to`, ensuring that users only see or manage
    the objects they are allowed to.
    """

    def get_queryset(self) -> AccessQuerySet[T]:
        return AccessQuerySet(self.model, using=self._db)

    def visible_to(self, user):
        return self.get_queryset().visible_to(user)

    def manage_to(self, user):
        return self.get_queryset().manage_to(user)

    @staticmethod
    def visible_eve_characters(user):
        """EveCharacters the user may pick."""
        qs = EveCharacter.objects.get_queryset()
        if GeneralManager.has_admin_access(user):
            logger.debug("Returning all characters for %s.", user)
            return qs.all()

        if not getattr(user.profile, "main_character", None):
            logger.debug("User %s has no main character. Nothing visible.", user)
            return qs.none()

        return qs.filter(character_ownership__user=user)
