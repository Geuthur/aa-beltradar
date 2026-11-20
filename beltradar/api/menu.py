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
            "menu/",
            response={
                HTTPStatus.OK: schema.MenuSchema,
                HTTPStatus.FORBIDDEN: schema.ErrorSchema,
            },
            tags=self.tags,
            summary="Get Belt Radar navigation menu",
        )
        def get_menu(request):
            try:
                character_id = request.user.profile.main_character.character_id
            except AttributeError:
                character_id = 0

            left_menu: list[schema.MenuLink] = []
            left_menu.append(schema.MenuLink(name=_("Belt Radar"), link="/"))
            left_menu.append(
                schema.MenuLink(
                    name=_("My Sessions"), link=f"/my-belt-radar/{character_id}/"
                )
            )
            left_menu.append(schema.MenuLink(name=_("Settings"), link="/settings/"))
            right_menu: list[schema.MenuLink] = []
            return schema.MenuSchema(left_links=left_menu, right_links=right_menu)
