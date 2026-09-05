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
from beltradar.api.helpers.core import get_belt_timer_or_none, get_session_or_none
from beltradar.api.helpers.icons import (
    belt_timer_manage_action_icons,
    get_belt_timer_status_icon,
)
from beltradar.models.beltradar import (
    BeltTimer,
    generate_unique_public_id,
)
from beltradar.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


class BeltRadarApiEndpoints:
    tags = ["Belt-Timer"]

    # pylint: disable=too-many-statements
    def __init__(self, api: NinjaAPI):

        @api.get(
            "view/my-belt-timer/{character_id}/",
            response={
                HTTPStatus.OK: list[schema.BeltTimerSchema],
                HTTPStatus.FORBIDDEN: dict,
                HTTPStatus.NOT_FOUND: dict,
            },
            tags=self.tags,
        )
        def get_my_belt_timer(request, character_id: int):
            """
            Get belt timer details for the user's belt timer.

            This Endpoint allows users to retrieve a list of all belt timers associated with their character ID.
            The user must have permission to access the belt timer, and the belt timer must exist.

            Args:
                character_id (int): The character ID of the user.
            Returns:
                200: A list of belt timers in the API response format.
                403: An error message if the user does not have permission or the belt timer is not found.
                404: An error message if the belt timer is not found.
            """
            perms = False

            # Check if the character ID is in the list of visible characters for the current user
            visible_characters = BeltTimer.objects.visible_eve_characters(
                request.user
            ).values_list("character_id", flat=True)
            if character_id in visible_characters:
                perms = True

            # pylint: disable=duplicate-code
            if perms is False:
                return HTTPStatus.FORBIDDEN, {"error": _("Permission Denied.")}

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
                            raw=timer.is_public,
                            display=get_belt_timer_status_icon(timer=timer),
                            sort=str(timer.is_public),
                        ),
                        is_expired=timer.is_expired,
                        html=str(
                            belt_timer_manage_action_icons(
                                request=request,
                                timer=timer,
                            )
                        ),
                    )
                )
            return HTTPStatus.OK, belt_timer_list

        @api.get(
            "view/belt-timers/",
            response={
                HTTPStatus.OK: list[schema.BeltTimerSchema],
            },
            tags=self.tags,
        )
        def get_belt_timers(request):
            """
            Get belt timer details for public timers.

            This Endpoint allows users to retrieve a list of all public belt timers.
            If the user is a superuser, they will receive all belt timers regardless of ownership.

            Returns:
                200: A list of belt timers in the API response format.
            """
            # Retrieve all public belt timers
            belt_timers = BeltTimer.objects.visible_to(request.user)

            # Serialize the belt timers into the API response format
            belt_timer_list: list[schema.BeltTimerSchema] = []
            for timer in belt_timers:
                # Skip sessions where the owner or main character is not set
                if timer.owner is None or timer.owner.profile.main_character is None:
                    continue

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
                            raw=timer.is_public,
                            display=get_belt_timer_status_icon(timer=timer),
                            sort=str(timer.is_public),
                        ),
                        is_expired=timer.is_expired,
                        html=str(
                            belt_timer_manage_action_icons(
                                request=request,
                                timer=timer,
                            )
                        ),
                    )
                )
            return HTTPStatus.OK, belt_timer_list

        @api.post(
            "manage/belt-timer/create/",
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
                        "message": _("Belt timer added successfully."),
                    }
            msg = _("Invalid input data. Please check the format and try again.")
            return HTTPStatus.BAD_REQUEST, {"success": False, "message": msg}

        @api.post(
            "manage/belt-timer/{public_id}/create/",
            response={
                HTTPStatus.OK: dict,
                HTTPStatus.BAD_REQUEST: dict,
                HTTPStatus.FORBIDDEN: dict,
                HTTPStatus.NOT_FOUND: dict,
            },
            tags=self.tags,
        )
        def add_session_belt_timer(request, public_id: str):
            """
            Add a new survey timer to a survey session.

            This Endpoint allows users to add a new survey timer to an existing survey session.
            The user must have permission to add entries to the survey session, and the survey session must exist.

            Args:
                public_id (str): The public UUID of the survey session.
            Returns:
                200: A success message indicating the survey timer was added.
                400: An error message if the input data is invalid or cannot be parsed.
                403: An error message if the user does not have permission or the survey session is not found.
                404: An error message if the survey session is not found.
            """
            # Check if the user has permission to add entries to this survey session
            perms, session = get_session_or_none(request=request, public_id=public_id)
            # pylint: disable=duplicate-code
            if perms is False:
                return HTTPStatus.FORBIDDEN, {"error": _("Permission Denied.")}
            # pylint: disable=duplicate-code
            if perms is None:
                return HTTPStatus.NOT_FOUND, {
                    "error": _("Requested resource not found.")
                }

            belt_type, belt_size = session.br_snapshots.session_resolve_belt()

            if belt_type is None or belt_size is None:
                msg = _("Session does not have a valid belt type or size.")
                return HTTPStatus.BAD_REQUEST, {"error": msg}

            with transaction.atomic():
                timer = BeltTimer(
                    owner=request.user,
                    public_id=session.public_id,
                    belt_id=generate_unique_public_id(length=7),
                    belt_name=session.name,
                    belt_type=belt_type,
                    belt_size=belt_size,
                    session=session,
                )
                timer.owner = request.user
                timer.save()
                return HTTPStatus.OK, {
                    "success": True,
                    "message": _("Session Belt timer added successfully."),
                }
            msg = _("Invalid input data. Please check the format and try again.")
            return HTTPStatus.BAD_REQUEST, {"success": False, "message": msg}

        @api.post(
            "manage/belt-timer/{timer_id}/delete/",
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
            # pylint: disable=duplicate-code
            if perms is False:
                return HTTPStatus.FORBIDDEN, {"error": _("Permission Denied.")}
            # pylint: disable=duplicate-code
            if perms is None:
                return HTTPStatus.NOT_FOUND, {
                    "error": _("Requested resource not found.")
                }

            # Delete the belt timer
            try:
                timer.delete()
            except ObjectDoesNotExist:
                msg = _("Belt timer not found.")
                return HTTPStatus.NOT_FOUND, {"error": msg}

            # If the belt timer was deleted successfully, return a success message
            msg = _("Belt timer deleted successfully.")
            return HTTPStatus.OK, {"success": True, "message": msg}

        @api.post(
            "manage/belt-timer/{timer_id}/modify/{field}/value/{value}/",
            response={
                HTTPStatus.OK: dict,
                HTTPStatus.BAD_REQUEST: dict,
                HTTPStatus.FORBIDDEN: dict,
                HTTPStatus.NOT_FOUND: dict,
            },
            tags=self.tags,
        )
        def modify_belt_timer(request, timer_id: int, field: str, value: str):
            """
            Modify a specific field of a belt timer in a survey session.

            This Endpoint allows users to modify a specific field of a belt timer within a survey session.
            The user must have permission to modify the survey session, and the survey session must exist.

            Args:
                timer_id (int): The ID of the belt timer to modify.
                field (str): The field of the belt timer to modify.
                value (str): The new value to set for the specified field.
            Returns:
                200: A success message indicating the belt timer was modified.
                400: An error message if the input data is invalid or cannot be parsed.
                403: An error message if the user does not have permission or the session is not found.
                404: An error message if the belt timer is not found.
            """
            # Check if the survey session exists
            try:
                timer = BeltTimer.objects.get(pk=timer_id)
            except ObjectDoesNotExist:
                msg = _("Belt timer not found.")
                return HTTPStatus.NOT_FOUND, {"error": msg}

            # Check if the user has permission to modify this snapshot (by checking if they can modify the survey session)
            perms = get_belt_timer_or_none(
                request=request,
                character_id=timer.owner.profile.main_character.character_id,
            )[0]
            # pylint: disable=duplicate-code
            if perms is False:
                return HTTPStatus.FORBIDDEN, {"error": _("Permission Denied.")}
            # pylint: disable=duplicate-code
            if perms is None:
                return HTTPStatus.NOT_FOUND, {
                    "error": _("Requested resource not found.")
                }

            # Modify the specified field of the belt timer
            if hasattr(timer, field):
                setattr(timer, field, value)
                msg = _(f"Belt timer {field} updated successfully.")
                # Save the changes to the database
                try:
                    timer.save()
                except Exception as e:  # pylint: disable=broad-except
                    msg = _(f"Failed to update belt timer {field}: {str(e)}")
                    return HTTPStatus.BAD_REQUEST, {"error": msg}
                return HTTPStatus.OK, {"success": True, "message": msg}
            msg = _("Invalid Method")
            return HTTPStatus.BAD_REQUEST, {"error": msg}
