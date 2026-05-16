"""Models for General."""

# Django
from django.db import models
from django.utils.translation import gettext_lazy as _


class General(models.Model):
    """General model for app permissions"""

    class Meta:
        managed = False
        permissions = (
            ("basic_access", _("Can access this app, Belt Radar")),
            ("manage_access", _("Can manage Belt Radar")),
            ("admin_access", _("Admin access to Belt Radar")),
        )
        default_permissions = ()  # Remove standard permissions
