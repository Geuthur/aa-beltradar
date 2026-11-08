# Standard Library
from http import HTTPStatus

# Third Party
from ninja import NinjaAPI

# Django
from django.urls import reverse
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
            },
            tags=self.tags,
            summary="Get Belt Radar navigation menu",
        )
        def get_menu(request):
            try:
                character_id = request.user.profile.main_character.character_id
            except AttributeError:
                character_id = 0

            create_session = schema.ModalSchema(
                url=reverse("beltradar:api:add_session"),
                modal_id="beltradar-accept-create-session",
            )

            create_belt_timer = schema.ModalSchema(
                url=reverse("beltradar:api:add_belt_timer"),
                modal_id="beltradar-accept-create-belt-timer",
            )

            left_menu: list[schema.MenuLink] = []
            left_menu.append(schema.MenuLink(name=_("Belt Radar"), link="/"))
            left_menu.append(
                schema.MenuLink(
                    name=_("My Sessions"), link=f"/my-belt-radar/{character_id}/"
                )
            )
            left_menu.append(schema.MenuLink(name=_("Settings"), link="/settings/"))
            right_menu: list[schema.MenuLink] = []
            return schema.MenuSchema(
                left_links=left_menu,
                right_links=right_menu,
                modals=schema.MenuModalSchema(
                    create_session=create_session,
                    create_belt_timer=create_belt_timer,
                ),
            )
