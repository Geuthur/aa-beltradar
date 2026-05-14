# Third Party
from ninja import NinjaAPI

# Django
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# AA Belt Radar
from beltradar import __title__
from beltradar.api import schema
from beltradar.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


class CharacterApiEndpoints:
    tags = ["Belt Radar"]

    def __init__(self, api: NinjaAPI):
        pass