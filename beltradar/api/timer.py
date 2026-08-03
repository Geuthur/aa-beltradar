# Standard Library
import json
from http import HTTPStatus

# Third Party
from ninja import NinjaAPI

# Django
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# AA Belt Radar
from beltradar import __title__, forms
from beltradar.api import schema
from beltradar.api.helpers.core import get_belt_timer_or_none
from beltradar.api.helpers.icons import (
    get_belt_timer_manage_action_icons,
    get_timer_public_icon,
)
from beltradar.models.beltradar import (
    BeltTimer,
)
from beltradar.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


class BeltRadarBeltTimerApiEndpoints:
    tags = ["Belt-Timer"]

    # pylint: disable=too-many-statements
    def __init__(self, api: NinjaAPI):

        @api.get(
            "belt-timer/{character_id}/view/my-timer/",
            response={
                HTTPStatus.OK: list[schema.BeltTimerSchema],
                HTTPStatus.FORBIDDEN: dict,
                HTTPStatus.NOT_FOUND: dict,
            },
            tags=self.tags,
        )
        def get_my_belt_timer(request, character_id: int):
            """Get belt timer details for the user's belt timer."""
            # Check if the user has permission to add entries to this survey session
            perms = get_belt_timer_or_none(
                request=request,
                character_id=character_id,
            )[0]

            # Check if the user has permission to access this resource
            if perms is False:
                return HTTPStatus.FORBIDDEN, {
                    "error": _("You do not have permission to access this resource.")
                }

            if perms is None:
                return HTTPStatus.NOT_FOUND, {
                    "error": _("No belt timer found for this character.")
                }

            # Retrieve all belt timers associated with the user's character ID
            belt_timers = BeltTimer.objects.filter(
                owner__profile__main_character__character_id=character_id
            )

            # Serialize the belt timers into the API response format
            belt_timer_list: list[schema.BeltTimerSchema] = []
            for timer in belt_timers:
                belt_timer_list.append(
                    schema.BeltTimerSchema(
                        public_id=str(timer.public_id),
                        belt_id=timer.belt_id,
                        belt_name=timer.belt_name,
                        belt_size=timer.get_belt_size_display,
                        belt_type=timer.get_belt_type_display,
                        eta=schema.DataTableSchema(
                            raw=timer.eta,
                            display=naturaltime(timer.eta) if timer.eta else "",
                            sort=str(timer.eta),
                        ),
                        public=schema.DataTableSchema(
                            raw=timer.public,
                            display=get_timer_public_icon(timer=timer),
                            sort=str(timer.public),
                        ),
                        html=str(
                            get_belt_timer_manage_action_icons(
                                request=request,
                                timer_id=timer.pk,
                                character_id=character_id,
                            )
                        ),
                    )
                )
            return HTTPStatus.OK, belt_timer_list

        @api.get(
            "belt-timer/view/timers/",
            response={
                HTTPStatus.OK: list[schema.BeltTimerSchema],
            },
            tags=self.tags,
        )
        def get_belt_timers(request):
            """Get belt timer details for public timers."""
            # Retrieve all public belt timers
            belt_timers = BeltTimer.objects.filter(public=True)

            # If the user is a superuser, retrieve all belt timers regardless of ownership
            if request.user.is_superuser:
                belt_timers = BeltTimer.objects.all()

            # Serialize the belt timers into the API response format
            belt_timer_list: list[schema.BeltTimerSchema] = []
            for timer in belt_timers:
                belt_timer_list.append(
                    schema.BeltTimerSchema(
                        public_id=str(timer.public_id),
                        belt_id=timer.belt_id,
                        belt_name=timer.belt_name,
                        belt_size=timer.get_belt_size_display,
                        belt_type=timer.get_belt_type_display,
                        eta=schema.DataTableSchema(
                            raw=timer.eta,
                            display=naturaltime(timer.eta) if timer.eta else "",
                            sort=str(timer.eta),
                        ),
                        public=schema.DataTableSchema(
                            raw=timer.public,
                            display=get_timer_public_icon(timer=timer),
                            sort=str(timer.public),
                        ),
                        html=str(
                            get_belt_timer_manage_action_icons(
                                request=request,
                                timer_id=timer.pk,
                                character_id=timer.owner.profile.main_character.character_id,
                            )
                        ),
                    )
                )
            return HTTPStatus.OK, belt_timer_list

        @api.post(
            "belt-timer/manage/add-timer/",
            response={
                HTTPStatus.OK: dict,
                HTTPStatus.BAD_REQUEST: dict,
                HTTPStatus.FORBIDDEN: dict,
                HTTPStatus.NOT_FOUND: dict,
            },
            tags=self.tags,
        )
        def add_belt_timer(request):
            """
            Add a new belt timer to a survey session.

            This Endpoint allows users to add a new belt timer to an existing survey session.
            The user must have permission to add entries to the survey session, and the survey session must exist.

            Args:
                public_id (str): The public UUID of the survey session.
                parsed_data: A JSON object containing the belt timer data, including belt ID, belt name, belt type, ETA, and snapshot identifier.
            Returns:
                200: A success message indicating the belt timer was added.
                400: An error message if the input data is invalid or cannot be parsed.
                403: An error message if the user does not have permission or the survey session is not found.
                404: An error message if the survey session is not found.
            """
            # Check if the user has permission to add entries to this survey session
            if not request.user.has_perm("beltradar.basic_access"):
                msg = _("Permission Denied.")
                return HTTPStatus.FORBIDDEN, {"error": msg}

            # Validate the form data
            form = forms.BeltTimerForm(data=json.loads(request.body))
            if form.is_valid():
                with transaction.atomic():
                    timer: BeltTimer = form.save(commit=False)
                    timer.owner = request.user
                    timer.save()
                    return HTTPStatus.OK, {
                        "success": True,
                        "message": _("Survey entry added successfully."),
                    }
            msg = _("Invalid input data. Please check the format and try again.")
            return HTTPStatus.BAD_REQUEST, {"success": False, "message": msg}

        @api.post(
            "belt-timer/{timer_id}/manage/delete-timer/",
            response={
                HTTPStatus.OK: dict,
                HTTPStatus.FORBIDDEN: dict,
                HTTPStatus.NOT_FOUND: dict,
            },
            tags=self.tags,
        )
        def delete_belt_timer(request, timer_id: int):
            """
            Delete a specific belt timer in a survey session.

            This Endpoint allows users to delete a specific belt timer within a survey session.
            The user must have permission to delete the survey session, and the survey session must exist.

            Args:
                timer_id (int): The ID of the belt timer to delete.
            Returns:
                200: A success message indicating the belt timer was deleted.
                403: An error message if the user does not have permission or the session is not found.
                404: An error message if the belt timer is not found.
            """
            # Check if the survey session exists
            try:
                timer = BeltTimer.objects.get(pk=timer_id)
            except ObjectDoesNotExist:
                msg = _("Belt timer not found.")
                return HTTPStatus.NOT_FOUND, {"error": msg}

            # Check if the user has permission to delete this snapshot (by checking if they can delete the survey session)
            perms = get_belt_timer_or_none(
                request=request,
                character_id=timer.owner.profile.main_character.character_id,
            )[0]
            if not perms:
                msg = _("Permission Denied.")
                return HTTPStatus.FORBIDDEN, {"error": msg}

            # Delete the belt timer
            try:
                timer.delete()
            except ObjectDoesNotExist:
                msg = _("Belt timer not found.")
                return HTTPStatus.NOT_FOUND, {"error": msg}

            # If the belt timer was deleted successfully, return a success message
            msg = _("Belt timer deleted successfully.")
            return HTTPStatus.OK, {"success": True, "message": msg}
