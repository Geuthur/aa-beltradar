# Standard Library
import json
from http import HTTPStatus

# Third Party
from ninja import NinjaAPI

# Django
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from eve_sde.models import ItemType

# AA Belt Radar
from beltradar import __title__, forms
from beltradar.api import schema
from beltradar.api.helpers.charts import (
    generate_apex_chart_mining_data,
    generate_apex_chart_traffic_data,
)
from beltradar.api.helpers.core import (
    get_owner_or_none,
    get_public_id_or_none,
)
from beltradar.api.helpers.icons import (
    get_snapshot_delete_button,
    survey_manage_action_icons,
)
from beltradar.helpers.eveonline import get_character_portrait_url
from beltradar.models.beltradar import (
    BeltSurveyEntry,
    BeltSurveySession,
    EveMarketPrice,
)
from beltradar.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


class BeltRadarSurveyApiEndpoints:
    tags = ["Survey"]

    def session_stats(self, session: BeltSurveySession) -> schema.SnapShotStatsSchema:
        """
        Calculate belt stats for the latest snapshot of the given survey session.

        This method retrieves the first and last entries for the session, calculates belt size, remaining volume, mined volume, and other statistics, and returns them in a SnapShotStatsSchema object.

        Args:
            session (BeltSurveySession): The survey session for which to calculate stats.
        Returns:
            SnapShotStatsSchema: An object containing calculated statistics for the survey session.
        """
        # Get the first and last entries for the session
        f_entries = session.br_entries.filter(snapshot=session.snapshots.first())
        l_entries = session.br_entries.filter(snapshot=session.snapshots.last())

        # Calculate belt size, remaining volume, and mined volume
        belt_size_m3 = f_entries.belt_size_m3()
        belt_left_m3 = l_entries.belt_size_m3()
        rate_per_s = session.br_entries.rate_per_s(
            first_entries=f_entries, second_entries=l_entries
        )
        progress_percent = round(session.br_entries.session_progress_percentage(), 2)

        belt_type, belt_size = session.br_entries.session_resolve_belt()

        return schema.SnapShotStatsSchema(
            belt_volume=belt_size_m3,
            belt_volume_left_m3=belt_left_m3,
            remaining_asteroids=l_entries.asteroid_count(),
            total_asteroids=f_entries.asteroid_count(),
            progress_percent=progress_percent,
            mining_rate_m3_per_s=round(rate_per_s, 4),
            finish_eta=session.br_entries.session_finish_eta(),
            excpected_belt_type=belt_type.label if belt_type else None,
            excpected_belt_size=belt_size.label if belt_size else None,
        )

    # pylint: disable=too-many-statements
    def __init__(self, api: NinjaAPI):
        @api.get(
            "view/session/{public_id}/",
            response={
                HTTPStatus.OK: schema.BeltSurveySessionSchema,
                HTTPStatus.FORBIDDEN: dict,
                HTTPStatus.NOT_FOUND: dict,
            },
            tags=self.tags,
        )
        def get_survey_session(request, public_id: str):
            """
            Get survey session details for a specific public_id.

            This Endpoint allows users to retrieve details of a specific survey session identified by its public_id.
            The user must have permission to access the survey session, and the survey session must exist.

            Args:
                public_id (str): The public UUID of the survey session.
            Returns:
                200: A dictionary containing the survey session details in the API response format.
                403: An error message if the user does not have permission to access the survey session.
                404: An error message if the survey session is not found or not public.
            """
            if not request.user.has_perm("beltradar.basic_access"):
                return HTTPStatus.FORBIDDEN, {
                    "error": _("You do not have permission to access this resource.")
                }

            try:
                session = BeltSurveySession.objects.get(public_id=public_id)
            except ObjectDoesNotExist:
                return HTTPStatus.NOT_FOUND, {
                    "error": _("Survey session not found or not public.")
                }

            survey_session_data = schema.BeltSurveySessionSchema(
                public_id=str(session.public_id),
                name=session.name,
                created_at=session.created_at,
                owner=str(session.owner),
                html=str(
                    survey_manage_action_icons(request=request, public_id=public_id)
                ),
            )
            return HTTPStatus.OK, survey_session_data

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
            Get all survey sessions for the current user.

            This Endpoint allows users to retrieve a list of all survey sessions associated with their character ID.
            The user must have permission to access the survey sessions.

            Args:
                character_id (int): The character ID of the user.
            Returns:
                200: A list of survey sessions in the API response format.
                403: An error message if the user does not have permission to access the survey sessions.
                404: An error message if no survey sessions are found for the character.
            """
            perms = get_owner_or_none(request=request, character_id=character_id)[0]

            if perms is False:
                return HTTPStatus.FORBIDDEN, {"error": _("Permission Denied.")}

            sessions = BeltSurveySession.objects.filter(
                owner__profile__main_character__character_id=character_id
            ).order_by("-created_at")
            survey_list: list[schema.BeltSurveySessionSchema] = []
            for session in sessions:
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
                    html=str(
                        survey_manage_action_icons(
                            request=request, public_id=session.public_id
                        )
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
        def get_sessions(request):
            """
            Get all survey sessions for the current user.

            This Endpoint allows users to retrieve a list of all survey sessions that are visible to them.
            The user must have permission to access the survey sessions.

            Returns:
                200: A list of survey sessions in the API response format.
                403: An error message if the user does not have permission to access the survey sessions.
                404: An error message if no survey sessions are found for the user.
            """
            # Get all sessions visible to the user, ordered by creation date descending
            sessions = BeltSurveySession.objects.visible_to(request.user).order_by(
                "-created_at"
            )

            # Serialize sessions into the API response format
            survey_list: list[schema.BeltSurveySessionSchema] = []
            for session in sessions:
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
                    html=str(
                        survey_manage_action_icons(
                            request=request, public_id=session.public_id
                        )
                    ),
                )
                survey_list.append(survey_session_data)
            return HTTPStatus.OK, survey_list

        @api.get(
            "view/session/{public_id}/snapshot/last_entry/",
            response={
                HTTPStatus.OK: schema.SnapShotSchema,
                HTTPStatus.FORBIDDEN: dict,
                HTTPStatus.NOT_FOUND: dict,
            },
            tags=self.tags,
        )
        def get_survey_entry(request, public_id: str):
            """
            Get all survey entries for the current user.

            Args:
                public_id (str): The public ID of the survey session.
            Returns:
                200: The last survey entry for the current user in the API response format.
                403: An error message if the user does not have permission to access the survey session.
                404: An error message if the survey session is not found.
            """
            if not request.user.has_perm("beltradar.basic_access"):
                return HTTPStatus.FORBIDDEN, {
                    "error": _("You do not have permission to access this resource.")
                }

            # Check if the survey session exists
            try:
                session = BeltSurveySession.objects.get(public_id=public_id)
            except ObjectDoesNotExist:
                return HTTPStatus.NOT_FOUND, {
                    "error": _("Survey session not found or not public.")
                }

            last_entries = session.br_entries.filter(
                snapshot=session.snapshots.last()
            )  # Get entries for the last timestamp

            # Aggregate data for the last snapshot
            aggregated_items = BeltSurveyEntry.objects.aggregate_entries_by_ore(
                entries=last_entries
            )

            # Create a list of survey entries for the current user, ordered by timestamp
            snapshot_list: list[schema.OreSchema] = []
            for ore_name, ore_data in aggregated_items.items():
                ore_data = schema.OreSchema(
                    portrait=ore_data["portrait"],
                    name=ore_name,
                    units=ore_data["units"],
                    volume_m3=ore_data["volume_left"],
                    price_isk=ore_data["price_per_m3"],
                    price_compressed=ore_data["price_cmp_per_m3"],
                    income_per_h=ore_data["income_per_h"],
                    income_cmp_per_h=ore_data["income_cmp_per_h"],
                    timestamp=ore_data["timestamp"],
                    snapshot=ore_data["snapshot"],
                )
                snapshot_list.append(ore_data)

            return HTTPStatus.OK, schema.SnapShotSchema(
                session=schema.SessionSchema(
                    public_id=str(session.public_id),
                    name=session.name,
                    created_at=session.created_at,
                    owner=str(session.owner),
                    first_entry_timestamp=session.first_timestamp,
                    last_entry_timestamp=session.last_timestamp,
                ),
                snapshot=session.snapshots.last(),
                entries=snapshot_list,
                charts=generate_apex_chart_mining_data(session=session),
                traffic=generate_apex_chart_traffic_data(session=session),
                stats=self.session_stats(session=session),
                delete_html=str(
                    get_snapshot_delete_button(
                        request=request,
                        public_id=session.public_id,
                        snapshot=session.snapshots.last(),
                    )
                ),
            )

        @api.post(
            "manage/delete-session/{public_id}/",
            response={
                HTTPStatus.OK: dict,
                HTTPStatus.FORBIDDEN: dict,
                HTTPStatus.NOT_FOUND: dict,
            },
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
            try:
                session = BeltSurveySession.objects.get(public_id=public_id)
            except ObjectDoesNotExist:
                msg = _("Survey session not found.")
                return HTTPStatus.NOT_FOUND, {"error": msg}

            # Check if the user has permission to delete this survey session
            perms = get_public_id_or_none(
                request=request,
                public_id=public_id,
            )[0]
            if not perms:
                msg = _("Permission Denied.")
                return HTTPStatus.FORBIDDEN, {"error": msg}

            # Delete the survey session and all associated entries
            session.delete()
            # If the session was deleted successfully, return a success message
            msg = _("Survey session and all associated entries deleted successfully.")
            return HTTPStatus.OK, {"success": True, "message": msg}

        @api.post(
            "manage/delete-snapshot/{public_id}/snapshot/{snapshot}/",
            response={
                HTTPStatus.OK: dict,
                HTTPStatus.FORBIDDEN: dict,
                HTTPStatus.NOT_FOUND: dict,
            },
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
            try:
                session = BeltSurveySession.objects.get(public_id=public_id)
            except ObjectDoesNotExist:
                msg = _("Survey session not found.")
                return HTTPStatus.NOT_FOUND, {"error": msg}

            # Check if the user has permission to delete this snapshot (by checking if they can delete the survey session)
            perms = get_owner_or_none(
                request=request,
                character_id=session.owner.profile.main_character.character_id,
            )[0]
            if not perms:
                msg = _("Permission Denied.")
                return HTTPStatus.FORBIDDEN, {"error": msg}

            deleted_count = session.br_entries.filter(snapshot=snapshot).delete()[0]
            if deleted_count == 0:
                msg = _("No entries found for the given snapshot.")
                return HTTPStatus.NOT_FOUND, {"error": msg}

            # If entries were deleted successfully, return a success message
            msg = _("Snapshot deleted successfully.")
            return HTTPStatus.OK, {"success": True, "message": msg}

        @api.post(
            "manage/add-survey-entry/{public_id}/",
            response={
                HTTPStatus.OK: dict,
                HTTPStatus.BAD_REQUEST: dict,
                HTTPStatus.FORBIDDEN: dict,
                HTTPStatus.NOT_FOUND: dict,
            },
            tags=self.tags,
        )
        def add_survey_entry(
            request, public_id: str
        ):  # pylint: disable=too-many-locals
            """
            Add a new survey entry to a survey session.

            This Endpoint allows users to add a new survey entry to an existing survey session.
            The user must have permission to add entries to the survey session, and the survey session must exist.

            Args:
                public_id (str): The public UUID of the survey session.
                parsed_data: A JSON object containing the survey entry data, including ore name, units, volume, price, timestamp, and snapshot identifier.
            Returns:
                200: A success message indicating the survey entry was added.
                400: An error message if the input data is invalid or cannot be parsed.
                403: An error message if the user does not have permission or the session is not found.
                404: An error message if the survey session is not found.
            """
            # Check if the survey session exists
            try:
                session = BeltSurveySession.objects.get(public_id=public_id)
            except ObjectDoesNotExist:
                msg = _("Survey session not found.")
                return HTTPStatus.NOT_FOUND, {"error": msg}

            # Check if the user has permission to add entries to this survey session
            perms = get_public_id_or_none(
                request=request,
                public_id=public_id,
            )[0]

            if not perms:
                msg = _("Permission Denied.")
                return HTTPStatus.FORBIDDEN, {"error": msg}

            # Validate the form data
            form = forms.AddSurveyForm(data=json.loads(request.body))
            if not form.is_valid():
                try:
                    msg = form.errors.as_json(escape_html=False)
                except IndexError:
                    msg = _(
                        "Invalid input data. Please check the format and try again."
                    )
                return HTTPStatus.BAD_REQUEST, {"success": False, "message": msg}

            survey_entries = []
            survey_data: schema.OreSchemaResponse = form.cleaned_data.get(
                "raw_data", None
            )

            # If no valid entries were parsed from the input data, return an error message
            if not survey_data or not survey_data.entries:
                msg = _("No valid entries to add. Errors:") + " , ".join(
                    survey_data.errors if survey_data else ["No data"]
                )
                return HTTPStatus.BAD_REQUEST, {"success": False, "message": msg}

            missing_types = []
            names = [item.name for item in survey_data.entries]
            unique_names = sorted(set(names))
            unique_name_set = set(unique_names)

            # Fetch all relevant ItemType records in a single query to minimize database hits
            compressed_names = [f"Compressed {name}" for name in unique_names]
            type_rows = ItemType.objects.filter(
                name__in=(unique_names + compressed_names)
            ).values("id", "name")

            eve_type_ids = {}
            compressed_type_ids = {}
            for row in type_rows:
                item_name = row["name"]
                item_id = row["id"]
                if item_name in unique_name_set:
                    eve_type_ids[item_name] = item_id
                elif item_name.startswith("Compressed "):
                    base_name = item_name[11:]
                    if base_name in unique_name_set:
                        compressed_type_ids[base_name] = item_id

            all_type_ids = list(
                set(eve_type_ids.values()) | set(compressed_type_ids.values())
            )
            price_by_type_id = {
                row["eve_type_id"]: (row["average_price"] or 0)
                for row in EveMarketPrice.objects.filter(
                    eve_type_id__in=all_type_ids
                ).values("eve_type_id", "average_price")
            }

            # Create a set of existing type names for quick lookup
            existing_type_names = set(eve_type_ids.keys())

            for item in survey_data.entries:
                if item.name not in existing_type_names:
                    missing_types.append(item.name)
                    continue  # skip items with missing types

                eve_type_id = eve_type_ids[item.name]

                # Get price from EveMarketPrice if available, otherwise default to 0
                price = price_by_type_id.get(eve_type_id, 0)
                compressed_type_id = compressed_type_ids.get(item.name)
                compressed_price = (
                    price_by_type_id.get(compressed_type_id, 0)
                    if compressed_type_id
                    else 0
                )

                entry = BeltSurveyEntry(
                    session=session,
                    recorded_by=request.user,
                    eve_type_id=eve_type_id,
                    units=item.units,
                    volume_left=item.volume_m3,
                    price=price,
                    price_compressed=compressed_price,
                    note=(
                        f"Added via batch import. Missing types: {', '.join(missing_types)}"
                        if missing_types
                        else "Added via batch import."
                    ),
                    timestamp=item.timestamp,
                    snapshot=item.snapshot,
                )
                survey_entries.append(entry)

            if survey_entries:
                with transaction.atomic():
                    BeltSurveyEntry.objects.bulk_create(survey_entries)
                return HTTPStatus.OK, {
                    "success": True,
                    "message": _("Survey entry added successfully."),
                }
            return HTTPStatus.BAD_REQUEST, {
                "success": False,
                "message": _("No valid entries to add. Missing types:")
                + " , ".join(missing_types)
                + ". Errors: "
                + ", ".join(survey_data.errors if survey_data else ["No data"]),
            }
