"""Models for General."""

# Django
from django.db import models
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.authentication.models import User

# AA Belt Radar
from beltradar.managers.general import GeneralManager


class General(models.Model):
    """General model for app permissions"""

    objects = GeneralManager()

    class Meta:
        managed = False
        verbose_name = "AA-Belt-Radar"
        verbose_name_plural = "AA-Belt-Radar"
        permissions = (
            ("basic_access", _("Can access this app, Belt Radar")),
            ("manage_access", _("Can manage Belt Radar")),
            ("admin_access", _("Admin access to Belt Radar")),
        )
        default_permissions = ()  # Remove standard permissions


class UserSettings(models.Model):
    class Meta:
        default_permissions = ()  # Remove standard permissions

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="+",
    )

    disable_notifications = models.BooleanField(default=False)
