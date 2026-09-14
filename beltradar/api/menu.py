# Standard Library
from http import HTTPStatus

# Third Party
from ninja import NinjaAPI

# Django
from django.utils.translation import gettext as _

# AA Belt Radar
from beltradar.api import schema


class BeltRadarApiEndpoints:
    tags = ["Survey"]

    # pylint: disable=too-many-statements
    def __init__(self, api: NinjaAPI):
        @api.get(
            "view/menu/",
            response={
                HTTPStatus.OK: list[schema.MenuLink],
            },
            tags=self.tags,
        )
        def get_menu(request):
            try:
                character_id = request.user.profile.main_character.character_id
            except AttributeError:
                character_id = 0
            menu_list = []
            menu_list.append(schema.MenuLink(name=_("Belt Radar"), link="/"))
            menu_list.append(
                schema.MenuLink(
                    name=_("My Sessions"), link=f"/my-belt-radar/{character_id}/"
                )
            )
            menu_list.append(schema.MenuLink(name=_("Settings"), link="/settings/"))
            return menu_list
