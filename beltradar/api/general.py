# Standard Library
from http import HTTPStatus

# Third Party
from ninja import NinjaAPI

# Django
from django.utils.translation import gettext as _

# AA Belt Radar
from beltradar.api import schema
from beltradar.helpers.eveonline import get_character_portrait_url
from beltradar.models.beltradar import UserSettings
from beltradar.models.general import General


class BeltRadarApiEndpoints:
    tags = ["Survey"]

    # pylint: disable=too-many-statements
    def __init__(self, api: NinjaAPI):
        @api.get(
            "user/",
            response={
                HTTPStatus.OK: schema.UserData,
                HTTPStatus.FORBIDDEN: schema.ErrorSchema,
            },
            tags=self.tags,
            summary="Get current user",
        )
        def get_user(request):
            if not General.has_perm(request.user, General.Permission.BASIC_ACCESS):
                return HTTPStatus.FORBIDDEN, {"error": _("Permission Denied.")}

            try:
                character = request.user.profile.main_character
                character_id = character.character_id
                character_name = character.character_name
                corporation_id = character.corporation_id
                corporation_name = character.corporation_name
                alliance_id = character.alliance_id
                alliance_name = character.alliance_name
            except AttributeError:
                character_id = 0
                character_name = ""
                corporation_id = 0
                corporation_name = ""
                alliance_id = None
                alliance_name = None

            portrait_url = (
                get_character_portrait_url(
                    character_id=character_id,
                    character_name=character_name,
                    as_html=False,
                )
                if character_id
                else None
            )

            return HTTPStatus.OK, schema.UserData(
                user_id=request.user.id,
                character_id=character_id,
                character_name=character_name,
                corporation_id=corporation_id,
                corporation_name=corporation_name,
                alliance_id=alliance_id,
                alliance_name=alliance_name,
                portrait=portrait_url,
                is_admin=request.user.is_superuser,
            )

        @api.get(
            "settings/",
            response={
                HTTPStatus.OK: schema.UserSettingsSchema,
                HTTPStatus.FORBIDDEN: schema.ErrorSchema,
            },
            tags=self.tags,
            summary="Get current user's settings",
        )
        def get_user_settings(request):
            if not General.has_perm(request.user, General.Permission.BASIC_ACCESS):
                return HTTPStatus.FORBIDDEN, {"error": _("Permission Denied.")}

            settings = UserSettings.objects.get_or_create(user=request.user)[0]
            return schema.UserSettingsSchema(
                disable_notifications=settings.disable_notifications
            )

        @api.put(
            "settings/",
            response={
                HTTPStatus.OK: schema.UserSettingsSchema,
                HTTPStatus.FORBIDDEN: schema.ErrorSchema,
            },
            tags=self.tags,
            summary="Update current user's settings",
        )
        def update_user_settings(request, payload: schema.UserSettingsUpdateRequest):
            if not General.has_perm(request.user, General.Permission.BASIC_ACCESS):
                return HTTPStatus.FORBIDDEN, {"error": _("Permission Denied.")}

            settings = UserSettings.objects.get_or_create(user=request.user)[0]
            settings.disable_notifications = payload.disable_notifications
            settings.save(update_fields=["disable_notifications"])
            return schema.UserSettingsSchema(
                disable_notifications=settings.disable_notifications
            )
