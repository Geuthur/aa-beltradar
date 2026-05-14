"""App Configuration"""

# Django
from django.apps import AppConfig

# AA Belt Radar
from beltradar import __version__


class BeltRadarConfig(AppConfig):
    """App Config"""

    default_auto_field = "django.db.models.AutoField"
    name = "beltradar"
    label = "beltradar"
    verbose_name = f"Belt Radar v{__version__}"
