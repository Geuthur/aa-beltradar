# Third Party
from ninja import NinjaAPI

# Django
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# AA Belt Radar
from beltradar import __title__
from beltradar.api import schema
from beltradar.api.helpers.core import get_owner_or_none, get_public_id_or_none
from beltradar.api.helpers.icons import (
    get_snapshot_delete_button,
    get_survey_manage_action_icons,
)
from beltradar.helpers.eveonline import get_icon_render_url
from beltradar.models.beltradar import BeltSurveySession
from beltradar.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


class BeltRadarSurveyApiEndpoints:
    tags = ["Survey"]

    def __init__(self, api: NinjaAPI):
        @api.get(
            "view/session/{public_id}/",
            response={200: schema.BeltSurveySessionSchema, 403: str},
            tags=self.tags,
        )
        def get_survey_session(request, public_id: str):
            """Get survey session details for a specific public_id."""
            if not request.user.has_perm("beltradar.basic_access"):
                return 403, _("You do not have permission to access this resource.")

            session = BeltSurveySession.objects.filter(public_id=public_id).first()
            if not session:
                return 403, _("Survey session not found or not public.")

            survey_session_data = schema.BeltSurveySessionSchema(
                public_id=str(session.public_id),
                name=session.name,
                created_at=session.created_at,
                owner=str(session.owner),
                html=str(
                    get_survey_manage_action_icons(request=request, public_id=public_id)
                ),
            )
            return 200, survey_session_data

        @api.get(
            "view/my-sessions/{character_id}/",
            response={200: list[schema.BeltSurveySessionSchema], 403: dict, 404: dict},
            tags=self.tags,
        )
        def get_my_sessions(request, character_id: int):
            """Get all survey sessions for the current user."""
            perms = get_owner_or_none(request=request, character_id=character_id)[0]

            if perms is False:
                return 403, {"error": _("Permission Denied.")}

            sessions = BeltSurveySession.objects.filter(
                owner__profile__main_character__character_id=character_id
            ).order_by("-created_at")
            survey_list: list[schema.BeltSurveySessionSchema] = []
            for session in sessions:
                survey_session_data = schema.BeltSurveySessionSchema(
                    public_id=str(session.public_id),
                    name=session.name,
                    created_at=session.created_at,
                    owner=str(session.owner),
                    html=str(
                        get_survey_manage_action_icons(
                            request=request, public_id=session.public_id
                        )
                    ),
                )
                survey_list.append(survey_session_data)
            return 200, survey_list

        @api.get(
            "view/session/{public_id}/entries/",
            response={200: list[schema.OreSchemaList], 403: str},
            tags=self.tags,
        )
        def get_survey_entries(request, public_id: str):
            """Get all survey entries for the current user."""
            if not request.user.has_perm("beltradar.basic_access"):
                return 403, _("You do not have permission to access this resource.")

            session = BeltSurveySession.objects.filter(public_id=public_id).first()
            if not session:
                return 403, _("Survey session not found or not public.")

            survey_entries = session.br_entries.select_related(
                "eve_type"
            ).grouped_by_time()
            # Create a list of survey entries for the current user, ordered by timestamp
            survey_list: list[schema.OreSchemaList] = []
            for entries in survey_entries:
                ore_list = []
                for entry in entries:
                    ore_data = schema.OreSchema(
                        portrait=(
                            get_icon_render_url(type_id=entry.eve_type.id, as_html=True)
                            if entry.eve_type
                            else None
                        ),
                        name=entry.eve_type.name if entry.eve_type else "Unknown",
                        units=entry.units or 0,
                        volume_m3=entry.volume_left or 0,
                        price_isk=entry.price or 0.0,
                        price_compressed=entry.price_compressed or None,
                        timestamp=entry.timestamp,
                        snapshot=entry.snapshot,
                    )
                    ore_list.append(ore_data)
                survey_list.append(
                    schema.OreSchemaList(
                        snapshot=entries[0].snapshot,
                        timestamp=entries[0].timestamp,
                        entries=ore_list,
                        delete_html=str(
                            get_snapshot_delete_button(
                                request=request,
                                public_id=public_id,
                                snapshot=entries[0].snapshot,
                            )
                        ),
                    )
                )
            return 200, survey_list

        @api.get(
            "view/session/{public_id}/snapshot/last_entry/",
            response={200: schema.OreSchemaList, 403: str},
            tags=self.tags,
        )
        def get_survey_entry(request, public_id: str):
            """Get all survey entries for the current user."""
            if not request.user.has_perm("beltradar.basic_access"):
                return 403, _("You do not have permission to access this resource.")

            # Check if the survey session exists
            session = BeltSurveySession.objects.filter(public_id=public_id).first()
            if not session:
                return 403, _("Survey session not found or not public.")

            # Get the most recent survey entry for this session (if any)
            entries = (
                session.br_entries.select_related("eve_type")
                .order_by("-timestamp")
                .filter(snapshot=session.last_entry_snapshot())
            )

            # Create a list of survey entries for the current user, ordered by timestamp
            snapshot_list: list[schema.OreSchema] = []
            for entry in entries:
                ore_data = schema.OreSchema(
                    portrait=(
                        get_icon_render_url(type_id=entry.eve_type.id, as_html=True)
                        if entry.eve_type
                        else None
                    ),
                    name=entry.eve_type.name if entry.eve_type else "Unknown",
                    units=entry.units or 0,
                    volume_m3=entry.volume_left or 0,
                    price_isk=entry.price or 0.0,
                    price_compressed=entry.price_compressed or None,
                    timestamp=entry.timestamp,
                    snapshot=entry.snapshot,
                )
                snapshot_list.append(ore_data)
            return 200, schema.OreSchemaList(
                snapshot=entries[0].snapshot,
                timestamp=entries[0].timestamp,
                entries=snapshot_list,
                delete_html=str(
                    get_snapshot_delete_button(
                        request=request,
                        public_id=entries[0].session.public_id,
                        snapshot=entries[0].snapshot,
                    )
                ),
            )

        @api.post(
            "session/{public_id}/manage/delete/",
            response={200: dict, 403: dict, 404: dict},
            tags=self.tags,
        )
        def delete_survey_session(request, public_id: str):
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
            session = BeltSurveySession.objects.filter(public_id=public_id).first()
            if not session:
                msg = _("Survey session not found.")
                return 404, {"error": msg}

            # Check if the user has permission to delete this survey session
            perms = get_public_id_or_none(
                request=request,
                public_id=public_id,
            )[0]
            if not perms:
                msg = _("Permission Denied.")
                return 403, {"error": msg}

            # Delete the survey session and all associated entries
            session.delete()
            # If the session was deleted successfully, return a success message
            msg = _("Survey session and all associated entries deleted successfully.")
            return 200, {"success": True, "message": msg}

        @api.post(
            "session/{public_id}/snapshot/{snapshot}/manage/delete/",
            response={200: dict, 403: dict, 404: dict},
            tags=self.tags,
        )
        def delete_snapshot(request, public_id: str, snapshot: str):
            """
            Delete all survey entries for a specific snapshot in a survey session.

            This Endpoint allows users to delete all entries associated with a specific snapshot timestamp within a survey session.
            The user must have permission to delete the survey session, and the survey session must exist.

            Args:
                public_id (str): The public UUID of the survey session.
                snapshot (str): The timestamp of the snapshot to delete, in ISO format.
            Returns:
                200: A success message indicating the snapshot was deleted.
                403: An error message if the user does not have permission or the session is not found.
                404: An error message if no entries are found for the given snapshot.
            """
            # Check if the survey session exists
            session = BeltSurveySession.objects.filter(public_id=public_id).first()
            if not session:
                msg = _("Survey session not found.")
                return 404, {"error": msg}

            # Check if the user has permission to delete this snapshot (by checking if they can delete the survey session)
            perms = get_owner_or_none(
                request=request,
                character_id=session.owner.profile.main_character.character_id,
            )[0]
            if not perms:
                msg = _("Permission Denied.")
                return 403, {"error": msg}

            deleted_count = session.br_entries.filter(snapshot=snapshot).delete()[0]
            if deleted_count == 0:
                msg = _("No entries found for the given snapshot.")
                return 404, {"error": msg}

            # If entries were deleted successfully, return a success message
            msg = _("Snapshot deleted successfully.")
            return 200, {"success": True, "message": msg}
