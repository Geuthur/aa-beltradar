"""Models for General."""

# Django
from django.db import models
from django.utils.translation import gettext_lazy as _

# AA Belt Radar
from beltradar.managers import GeneralManager


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
