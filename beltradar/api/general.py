# Standard Library
from http import HTTPStatus

# Third Party
from ninja import NinjaAPI

# Django
from django.utils.translation import gettext as _

# AA Belt Radar
from beltradar import forms
from beltradar.api import schema
from beltradar.helpers.eveonline import get_character_portrait_url
from beltradar.models.beltradar import UserSettings


class BeltRadarApiEndpoints:
    tags = ["Survey"]

    # pylint: disable=too-many-statements
    def __init__(self, api: NinjaAPI):
        @api.get(
            "view/user/",
            response={
                HTTPStatus.OK: schema.UserData,
                HTTPStatus.FORBIDDEN: dict,
            },
            tags=self.tags,
        )
        def get_user(request):
            if not request.user.has_perm("beltradar.basic_access"):
                return HTTPStatus.FORBIDDEN, {"error": _("Permission Denied.")}

            try:
                character_id = request.user.profile.main_character.character_id
                character_name = request.user.profile.main_character.character_name
            except AttributeError:
                character_id = 0
                character_name = ""

            settings = UserSettings.objects.get_or_create(user=request.user)[0]

            portrait_url = (
                get_character_portrait_url(
                    character_id=character_id,
                    character_name=character_name,
                    as_html=False,
                )
                if character_id
                else None
            )

            return schema.UserData(
                user_id=request.user.id,
                character_id=character_id,
                character_name=character_name,
                portrait=portrait_url,
                notification=settings.disable_notifications,
            )

        @api.post(
            "modify/user/settings/",
            response={
                HTTPStatus.OK: dict,
                HTTPStatus.BAD_REQUEST: dict,
                HTTPStatus.FORBIDDEN: dict,
            },
            tags=self.tags,
        )
        def modify_user_settings(request):
            if not request.user.has_perm("beltradar.basic_access"):
                return HTTPStatus.FORBIDDEN, {"error": _("Permission Denied.")}

            settings = UserSettings.objects.get_or_create(user=request.user)[0]

            form = forms.UserSettingsForm(data=request.POST, instance=settings)
            if form.is_valid():
                form.save()
                return HTTPStatus.OK, {
                    "success": True,
                    "message": str(_("User settings updated successfully.")),
                }

            msg = _("Invalid input data. Please check the format and try again.")
            return HTTPStatus.BAD_REQUEST, {"success": False, "message": msg}
