"""Hook into Alliance Auth"""

# Django
# Django
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

from . import app_settings, urls
from .models import General


class BeltRadarMenuItem(MenuItemHook):
    """This class ensures only authorized users will see the menu entry"""

    def __init__(self):
        super().__init__(
            f"{app_settings.BELT_RADAR_APP_NAME}",
            "fas fa-book fa-fw",
            "beltradar:react_base",
            navactive=["beltradar:"],
        )

    def render(self, request):
        if General.objects.has_basic_access(request.user):
            return MenuItemHook.render(self, request)
        return ""


@hooks.register("menu_item_hook")
def register_menu():
    """Register the menu item"""

    return BeltRadarMenuItem()


@hooks.register("url_hook")
def register_urls():
    """Register app urls"""

    return UrlHook(urls, "beltradar", r"^beltradar/")
