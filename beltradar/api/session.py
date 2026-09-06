# Standard Library
import json
from http import HTTPStatus

# Third Party
from ninja import NinjaAPI

# Django
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# AA Belt Radar
from beltradar import __title__, forms
from beltradar.api import schema
from beltradar.api.helpers.core import (
    get_session_or_none,
)
from beltradar.api.helpers.icons import (
    get_session_status_icon,
    session_belt_timer_action_icons,
    session_manage_action_icons,
)
from beltradar.helpers.eveonline import get_character_portrait_url
from beltradar.models.beltradar import (
    BeltSurveySession,
    BeltSurveySnapshot,
)
from beltradar.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


class BeltRadarApiEndpoints:
    tags = ["Session"]

    def session_stats(self, session: BeltSurveySession) -> schema.SessionStatsSchema:
        """
        Calculate belt stats for the latest snapshot of the given survey session.

        This method retrieves the first and last entries for the session, calculates belt size, remaining volume, mined volume, and other statistics, and returns them in a SnapShotStatsSchema object.

        Args:
            session (BeltSurveySession): The survey session for which to calculate stats.
        Returns:
            SnapShotStatsSchema: An object containing calculated statistics for the survey session.
        """
        # Get the first and last entries for the session
        first_snapshot = session.br_snapshots.first()
        last_snapshot = session.br_snapshots.last()

        if not first_snapshot or not last_snapshot:
            return (
                schema.SessionStatsSchema()
            )  # Return an empty schema if no snapshots are found

        # Calculate belt size, remaining volume, and mined volume
        belt_size_m3 = (
            first_snapshot.asteroids.aggregate(models.Sum("volume_left"))[
                "volume_left__sum"
            ]
            or 0
        )
        belt_left_m3 = (
            last_snapshot.asteroids.aggregate(models.Sum("volume_left"))[
                "volume_left__sum"
            ]
            or 0
        )
        rate_per_s = session.br_snapshots.rate_per_s(
            first_snapshot=first_snapshot, second_snapshot=last_snapshot
        )
        progress_percent = round(
            session.br_snapshots.session_progress_percentage(
                asteroids=first_snapshot.asteroids,
                remaining_asteroids=last_snapshot.asteroids,
            ),
            2,
        )

        belt_type, belt_size = BeltSurveySnapshot.objects.filter(
            identifier=first_snapshot.identifier
        ).session_resolve_belt()

        return schema.SessionStatsSchema(
            belt_volume=belt_size_m3,
            belt_volume_left_m3=belt_left_m3,
            remaining_asteroids=last_snapshot.asteroid_count,
            total_asteroids=first_snapshot.asteroid_count,
            progress_percent=progress_percent,
            mining_rate_m3_per_s=round(rate_per_s, 4),
            finish_eta=session.br_snapshots.session_finish_eta(
                asteroids=first_snapshot.asteroids,
                remaining_asteroids=last_snapshot.asteroids,
            ),
            expected_belt_type=belt_type.label if belt_type else None,
            expected_belt_size=belt_size.label if belt_size else None,
        )

    # pylint: disable=too-many-statements
    def __init__(self, api: NinjaAPI):
        @api.get(
            "view/session/{public_id}/stats/",
            response={
                HTTPStatus.OK: schema.SessionSchema,
                HTTPStatus.FORBIDDEN: dict,
                HTTPStatus.NOT_FOUND: dict,
            },
            tags=self.tags,
        )
        def get_session_stats(request, public_id: str):
            """
            Get session statistics for a specific public_id.

            This Endpoint allows users to retrieve statistics of a specific survey session identified by its public_id.
            The user must have permission to access the survey session, and the survey session must exist.

            Args:
                public_id (str): The public UUID of the survey session.
            Returns:
                200: A dictionary containing the survey session statistics in the API response format.
                403: An error message if the user does not have permission to access the survey session.
                404: An error message if the survey session is not found or not public.
            """
            # pylint: disable=duplicate-code
            if not request.user.has_perm("beltradar.basic_access"):
                return HTTPStatus.FORBIDDEN, {"error": _("Permission Denied.")}

            try:
                session = BeltSurveySession.objects.get(public_id=public_id)
            except ObjectDoesNotExist:
                return HTTPStatus.NOT_FOUND, {
                    "error": _("Belt Session not found or not public.")
                }

            create_timer_html = str(
                session_belt_timer_action_icons(
                    request=request, public_id=session.public_id
                )
            )

            return HTTPStatus.OK, schema.SessionSchema(
                public_id=str(session.public_id),
                name=session.name,
                created_at=session.created_at,
                owner=str(session.owner),
                first_timestamp=session.first_timestamp,
                last_timestamp=session.last_timestamp,
                total_timestamps=session.br_snapshots.count(),
                public=schema.DataTableSchema(
                    raw=session.is_public,
                    display=get_session_status_icon(session=session),
                    sort=str(session.is_public),
                ),
                stats=self.session_stats(session=session),
                actions=schema.ActionSchema(
                    create=create_timer_html,
                ),
            )

        @api.get(
            "view/my-sessions/{character_id}/",
            response={
                HTTPStatus.OK: list[schema.BeltSurveySessionSchema],
                HTTPStatus.FORBIDDEN: dict,
                HTTPStatus.NOT_FOUND: dict,
            },
            tags=self.tags,
        )
        def get_my_sessions(request, character_id: int):
            """
            Get all sessions for the current user.

            This Endpoint allows users to retrieve a list of all sessions associated with their character ID.
            The user must have permission to access the sessions.

            Args:
                character_id (int): The character ID of the user.
            Returns:
                200: A list of sessions in the API response format.
                403: An error message if the user does not have permission to access the sessions.
                404: An error message if no sessions are found for the character.
            """
            perms = False

            # Check if the character ID is in the list of visible characters for the current user
            visible_characters = BeltSurveySession.objects.visible_eve_characters(
                request.user
            ).values_list("character_id", flat=True)
            if character_id in visible_characters:
                perms = True

            # pylint: disable=duplicate-code
            if perms is False:
                return HTTPStatus.FORBIDDEN, {"error": _("Permission Denied.")}

            sessions = BeltSurveySession.objects.filter(
                owner__profile__main_character__character_id=character_id
            ).order_by("-created_at")
            survey_list: list[schema.BeltSurveySessionSchema] = []
            for session in sessions:
                # Skip sessions where the owner or main character is not set
                if (
                    session.owner is None
                    or session.owner.profile.main_character is None
                ):
                    continue

                survey_session_data = schema.BeltSurveySessionSchema(
                    public_id=str(session.public_id),
                    name=session.name,
                    created_at=session.created_at,
                    owner=get_character_portrait_url(
                        character_id=session.owner.profile.main_character.character_id,
                        character_name=session.owner.profile.main_character.character_name,
                        as_html=True,
                        display_name=True,
                    ),
                    public=schema.DataTableSchema(
                        raw=session.is_public,
                        display=get_session_status_icon(session=session),
                        sort=str(session.is_public),
                    ),
                    html=str(
                        session_manage_action_icons(request=request, session=session)
                    ),
                )
                survey_list.append(survey_session_data)
            return HTTPStatus.OK, survey_list

        @api.get(
            "view/public-sessions/",
            response={
                HTTPStatus.OK: list[schema.BeltSurveySessionSchema],
            },
            tags=self.tags,
        )
        def get_public_sessions(request):
            """
            Get all sessions for the current user.

            This Endpoint allows users to retrieve a list of all sessions that are visible to them.
            The user must have permission to access the sessions.

            Returns:
                200: A list of sessions in the API response format.
                403: An error message if the user does not have permission to access the sessions.
                404: An error message if no sessions are found for the user.
            """
            # Get all sessions visible to the user, ordered by creation date descending
            sessions = BeltSurveySession.objects.visible_to(request.user).order_by(
                "-created_at"
            )

            # Serialize sessions into the API response format
            survey_list: list[schema.BeltSurveySessionSchema] = []
            for session in sessions:
                # Skip sessions where the owner or main character is not set
                if (
                    session.owner is None
                    or session.owner.profile.main_character is None
                ):
                    continue

                survey_session_data = schema.BeltSurveySessionSchema(
                    public_id=str(session.public_id),
                    name=session.name,
                    created_at=session.created_at,
                    owner=get_character_portrait_url(
                        character_id=session.owner.profile.main_character.character_id,
                        character_name=session.owner.profile.main_character.character_name,
                        as_html=True,
                        display_name=True,
                    ),
                    public=schema.DataTableSchema(
                        raw=session.is_public,
                        display=get_session_status_icon(session=session),
                        sort=str(session.is_public),
                    ),
                    html=str(
                        session_manage_action_icons(request=request, session=session)
                    ),
                )
                survey_list.append(survey_session_data)
            return HTTPStatus.OK, survey_list

        @api.post(
            "manage/session/add/",
            response={
                HTTPStatus.OK: dict,
                HTTPStatus.BAD_REQUEST: dict,
                HTTPStatus.FORBIDDEN: dict,
                HTTPStatus.NOT_FOUND: dict,
            },
            tags=self.tags,
        )
        def add_session(request):
            """
            Add a new session for the current user.

            This Endpoint allows users to create a new session associated with their character ID.
            The user must have permission to create sessions.

            Returns:
                200: A success message indicating the session was added.
                403: An error message if the user does not have permission to create sessions.
                400: An error message if the request data is invalid.
            """
            # Check if the user has permission to add entries to this survey session
            if not request.user.has_perm("beltradar.basic_access"):
                msg = _("Permission Denied.")
                return HTTPStatus.FORBIDDEN, {"error": msg}

            # Validate the form data
            form = forms.BeltSessionForm(data=json.loads(request.body))
            if form.is_valid():
                with transaction.atomic():
                    session = form.save(commit=False)
                    session.owner = request.user
                    session.save()
                    return HTTPStatus.OK, {
                        "success": True,
                        "message": _("Session added successfully."),
                    }
            msg = _("Invalid input data. Please check the format and try again.")
            return HTTPStatus.BAD_REQUEST, {"success": False, "message": msg}

        @api.post(
            "manage/session/{public_id}/delete/",
            response={
                HTTPStatus.OK: dict,
                HTTPStatus.FORBIDDEN: dict,
                HTTPStatus.NOT_FOUND: dict,
            },
            tags=self.tags,
        )
        def delete_session(request, public_id: str):
            """
            Delete an entire survey session and all its entries.

            This Endpoint allows users to delete an entire survey session along with all its associated entries.
            The user must have permission to delete the survey session, and the survey session must exist.

            Args:
                public_id (str): The public UUID of the survey session.
            Returns:
                200: A success message indicating the survey session was deleted.
                403: An error message if the user does not have permission or the session is not found.
                404: An error message if no entries are found for the given survey session.
            """
            # Check if the survey session exists
            try:
                session = BeltSurveySession.objects.get(public_id=public_id)
            except ObjectDoesNotExist:
                msg = _("Belt Session not found.")
                return HTTPStatus.NOT_FOUND, {"error": msg}

            # Check if the user has permission to delete this survey session
            perms = get_session_or_none(
                request=request,
                public_id=public_id,
            )[0]
            # pylint: disable=duplicate-code
            if perms is False:
                return HTTPStatus.FORBIDDEN, {"error": _("Permission Denied.")}
            # pylint: disable=duplicate-code
            if perms is None:
                return HTTPStatus.NOT_FOUND, {
                    "error": _("Requested resource not found.")
                }

            # Delete the survey session and all associated entries
            session.delete()
            # If the session was deleted successfully, return a success message
            msg = _("Session and all associated entries deleted successfully.")
            return HTTPStatus.OK, {"success": True, "message": msg}

        @api.post(
            "manage/session/{public_id}/modify/{field}/value/{value}/",
            response={
                HTTPStatus.OK: dict,
                HTTPStatus.FORBIDDEN: dict,
                HTTPStatus.NOT_FOUND: dict,
                HTTPStatus.BAD_REQUEST: dict,
            },
            tags=self.tags,
        )
        def modify_session(request, public_id: str, field: str, value: str):
            """
            Modify a specific session.

            This Endpoint allows users to modify a specific session.
            The user must have permission to modify the session, and the session must exist.

            Args:
                public_id (str): The public UUID of the session.
                field (str): The field of the session to modify.
                value (str): The new value to set for the specified field.
            Returns:
                200: A success message indicating the session was modified.
                403: An error message if the user does not have permission or the session is not found.
                404: An error message if the session does not exist.
                400: An error message if the request is malformed or invalid.
            """
            # Check if the session exists
            try:
                session = BeltSurveySession.objects.get(public_id=public_id)
            except ObjectDoesNotExist:
                msg = _("Belt Session not found.")
                return HTTPStatus.NOT_FOUND, {"error": msg}

            # Check if the user has permission to modify this session
            perms = get_session_or_none(
                request=request,
                public_id=public_id,
            )[0]
            # pylint: disable=duplicate-code
            if perms is False:
                return HTTPStatus.FORBIDDEN, {"error": _("Permission Denied.")}
            # pylint: disable=duplicate-code
            if perms is None:
                return HTTPStatus.NOT_FOUND, {
                    "error": _("Requested resource not found.")
                }

            # Modify the specified field of the belt session
            if hasattr(session, field):
                setattr(session, field, value)
                try:
                    session.save()
                except Exception as e:  # pylint: disable=broad-except
                    msg = _(f"Failed to update session {field}: {str(e)}")
                    return HTTPStatus.BAD_REQUEST, {"error": msg}
                msg = _(f"Session {field} updated successfully.")
                return HTTPStatus.OK, {"success": True, "message": msg}
            msg = _("Invalid Method.")
            return HTTPStatus.BAD_REQUEST, {"error": msg}
