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
            "view/menu/",
            response={
                HTTPStatus.OK: schema.MenuSchema,
            },
            tags=self.tags,
        )
        def get_menu(request):
            try:
                character_id = request.user.profile.main_character.character_id
            except AttributeError:
                character_id = 0

            create_session = schema.ModalSchema(
                url=reverse("beltradar:api:add_session"),
                icon="fa-solid fa-plus",
                title=str(_("Create Session")),
                text=str(_("Are you sure you want to create a new session?")),
                color="success",
                modal_id="beltradar-accept-create-session",
            )

            create_belt_timer = schema.ModalSchema(
                url=reverse("beltradar:api:add_belt_timer"),
                icon="fa-solid fa-plus",
                title=str(_("Create Belt Timer")),
                text=str(_("Are you sure you want to create a new belt timer?")),
                color="success",
                modal_id="beltradar-accept-create-belt-timer",
            )

            menu_list: list[schema.MenuLink] = []
            menu_list.append(schema.MenuLink(name=_("Belt Radar"), link="/"))
            menu_list.append(
                schema.MenuLink(
                    name=_("My Sessions"), link=f"/my-belt-radar/{character_id}/"
                )
            )
            menu_list.append(schema.MenuLink(name=_("Settings"), link="/settings/"))
            return schema.MenuSchema(
                links=menu_list,
                modals=schema.MenuModalSchema(
                    create_session=create_session,
                    create_belt_timer=create_belt_timer,
                ),
            )
