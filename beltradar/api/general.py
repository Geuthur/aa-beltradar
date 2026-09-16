# Standard Library
from http import HTTPStatus

# Third Party
from ninja import NinjaAPI

# Django
from django.utils.translation import gettext as _

# AA Belt Radar
from beltradar.api import schema
from beltradar.models.beltradar import UserSettings


class BeltRadarApiEndpoints:
    tags = ["Survey"]

    # pylint: disable=too-many-statements
    def __init__(self, api: NinjaAPI):
        @api.get(
            "view/user/",
            response={
                HTTPStatus.OK: schema.UserData,
            },
            tags=self.tags,
        )
        def get_user(request):
            try:
                character_id = request.user.profile.main_character.character_id
                character_name = request.user.profile.main_character.character_name
                settings = UserSettings.objects.get(user=request.user)
            except AttributeError:
                return HTTPStatus.BAD_REQUEST, {
                    "error": _("Failed to retrieve user data.")
                }

            return schema.UserData(
                user_id=request.user.id,
                character_id=character_id,
                character_name=character_name,
                notification=settings.disable_notifications,
            )
