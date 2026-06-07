# Standard Library
import json
from collections import defaultdict
from http import HTTPStatus

# Third Party
from ninja import NinjaAPI

# Django
from django.db import transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from eve_sde.models import ItemType

# AA Belt Radar
from beltradar import __title__, forms
from beltradar.api import schema
from beltradar.api.helpers.core import get_owner_or_none, get_public_id_or_none
from beltradar.api.helpers.icons import (
    get_snapshot_delete_button,
    get_survey_manage_action_icons,
)
from beltradar.helpers.eveonline import get_icon_render_url
from beltradar.models.beltradar import (
    BeltSurveyEntry,
    BeltSurveySession,
    EveMarketPrice,
)
from beltradar.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


class BeltRadarSurveyApiEndpoints:
    tags = ["Survey"]

    # pylint: disable=too-many-locals
    def ore_mining_stats(
        self,
        session: BeltSurveySession,
    ) -> schema.OreChartDataSchema:
        """Calculate per-ore mining progress from first to last snapshot."""
        ordered_entries = list(
            session.br_entries.select_related("eve_type").order_by("timestamp")
        )
        if len(ordered_entries) < 2:
            return schema.OreChartDataSchema()

        snapshots: dict[str, dict[str, object]] = {}
        for entry in ordered_entries:
            snapshot_key = str(
                entry.snapshot or entry.timestamp.replace(microsecond=0).isoformat()
            )
            if snapshot_key not in snapshots:
                snapshots[snapshot_key] = {
                    "timestamp": entry.timestamp,
                    "ores": defaultdict(float),
                }

            snapshot = snapshots[snapshot_key]
            if entry.timestamp > snapshot["timestamp"]:
                snapshot["timestamp"] = entry.timestamp

            ore_name = entry.eve_type.name if entry.eve_type else "Unknown"
            try:
                vol_left = float(getattr(entry, "volume_left", None) or 0.0)
            except (TypeError, ValueError):
                vol_left = 0.0
            snapshot["ores"][ore_name] += max(0.0, vol_left)

        ordered_snapshots = sorted(
            snapshots.values(), key=lambda item: item["timestamp"]
        )
        if len(ordered_snapshots) < 2:
            return schema.OreChartDataSchema()

        start_map = dict(ordered_snapshots[0]["ores"])
        end_map = dict(ordered_snapshots[-1]["ores"])

        ore_names = sorted(set(start_map.keys()) | set(end_map.keys()))
        categories: list[str] = []
        progress_data: list[float] = []

        for ore_name in ore_names:
            start_volume = max(0.0, float(start_map.get(ore_name, 0.0)))
            volume_left = max(0.0, float(end_map.get(ore_name, 0.0)))

            volume_mined = max(0.0, start_volume - volume_left)
            progress_percent = (
                min(100.0, max(0.0, (volume_mined / start_volume) * 100.0))
                if start_volume > 0
                else 0.0
            )
            categories.append(ore_name)
            progress_data.append(round(progress_percent, 2))
        return schema.OreChartDataSchema(
            categories=categories,
            series=[
                schema.OreMiningChartSeriesSchema(
                    name="Mined %",
                    data=progress_data,
                )
            ],
        )

    def session_stats(self, session: BeltSurveySession) -> schema.SnapShotStatsSchema:
        """Calculate belt stats for the latest snapshot of the given survey session."""
        return schema.SnapShotStatsSchema(
            belt_volume=session.belt_size_m3,
            belt_volume_left_m3=session.belt_left_m3,
            remaining_asteroids=session.remaining_asteroids,
            total_asteroids=session.total_asteroids,
            progress_percent=round(session.progress_percent, 2),
            mining_rate_m3_per_s=round(session.mining_rate_m3_per_s, 4),
            finish_eta=session.finish_eta,
        )

    def aggregate_entries_by_ore(
        self, entries: QuerySet[BeltSurveyEntry]
    ) -> dict[str, dict[str, object]]:
        """Aggregate survey entries by ore name, summing units and volume left."""
        aggregated: dict[str, dict[str, object]] = {}
        for entry in entries.select_related("eve_type"):
            ore_name = entry.eve_type.name if entry.eve_type else "Unknown"
            if ore_name not in aggregated:
                aggregated[ore_name] = {
                    "portrait": (
                        get_icon_render_url(type_id=entry.eve_type.id, as_html=True)
                        if entry.eve_type
                        else None
                    ),
                    "units": 0,
                    "volume_left": 0.0,
                    "price_per_m3": entry.price_per_m3,
                    "price_cmp_per_m3": entry.price_cmp_per_m3,
                    "income_per_h": entry.income_per_h,
                    "income_cmp_per_h": entry.income_cmp_per_h,
                    "timestamp": entry.timestamp,
                    "snapshot": entry.snapshot,
                }
            aggregated[ore_name]["units"] += entry.units
            try:
                vol_left = float(getattr(entry, "volume_left", None) or 0.0)
            except (TypeError, ValueError):
                vol_left = 0.0
            aggregated[ore_name]["volume_left"] += max(0.0, vol_left)
        return aggregated

    # pylint: disable=too-many-statements
    def __init__(self, api: NinjaAPI):
        @api.get(
            "view/session/{public_id}/",
            response={
                HTTPStatus.OK: schema.BeltSurveySessionSchema,
                HTTPStatus.FORBIDDEN: str,
            },
            tags=self.tags,
        )
        def get_survey_session(request, public_id: str):
            """Get survey session details for a specific public_id."""
            if not request.user.has_perm("beltradar.basic_access"):
                return 403, _("You do not have permission to access this resource.")

            try:
                session = BeltSurveySession.objects.get(public_id=public_id)
            except BeltSurveySession.DoesNotExist:
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
            response={
                HTTPStatus.OK: list[schema.BeltSurveySessionSchema],
                HTTPStatus.FORBIDDEN: dict,
                HTTPStatus.NOT_FOUND: dict,
            },
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
            "view/user-sessions/",
            response={
                HTTPStatus.OK: list[schema.BeltSurveySessionSchema],
                HTTPStatus.FORBIDDEN: dict,
                HTTPStatus.NOT_FOUND: dict,
            },
            tags=self.tags,
        )
        def get_user_sessions(request):
            """Get all survey sessions for the current user."""
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
            "view/session/{public_id}/snapshot/last_entry/",
            response={
                HTTPStatus.OK: schema.SnapShotSchema,
                HTTPStatus.FORBIDDEN: dict,
                HTTPStatus.NOT_FOUND: dict,
            },
            tags=self.tags,
        )
        def get_survey_entry(request, public_id: str):
            """Get all survey entries for the current user."""
            if not request.user.has_perm("beltradar.basic_access"):
                return 403, {
                    "error": _("You do not have permission to access this resource.")
                }

            # Check if the survey session exists
            try:
                session = BeltSurveySession.objects.get(public_id=public_id)
            except BeltSurveySession.DoesNotExist:
                return 404, {"error": _("Survey session not found or not public.")}

            # Get the most recent survey entry for this session (if any)
            last_entries = session.get_entries_for_snapshot(session.last_entry_snapshot)

            # Aggregate data for the last snapshot
            aggregated_items = self.aggregate_entries_by_ore(entries=last_entries)

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

            return 200, schema.SnapShotSchema(
                session=schema.SessionSchema(
                    public_id=str(session.public_id),
                    name=session.name,
                    created_at=session.created_at,
                    owner=str(session.owner),
                    first_entry_timestamp=session.first_entry_timestamp,
                    last_entry_timestamp=session.last_entry_timestamp,
                ),
                snapshot=session.last_entry_snapshot,
                entries=snapshot_list,
                charts=self.ore_mining_stats(session=session),
                stats=self.session_stats(session=session),
                delete_html=str(
                    get_snapshot_delete_button(
                        request=request,
                        public_id=session.public_id,
                        snapshot=session.last_entry_snapshot,
                    )
                ),
            )

        @api.post(
            "session/{public_id}/manage/delete/",
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
            except BeltSurveySession.DoesNotExist:
                msg = _("Survey session not found.")
                return 404, {"error": msg}

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
            "session/{public_id}/snapshot/{snapshot}/manage/delete/",
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
            except BeltSurveySession.DoesNotExist:
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
            "session/{public_id}/manage/add/",
            response={
                HTTPStatus.OK: dict,
                HTTPStatus.BAD_REQUEST: dict,
                HTTPStatus.FORBIDDEN: dict,
                HTTPStatus.NOT_FOUND: dict,
            },
            tags=self.tags,
        )
        def add_survey_entry(request, public_id: str):
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
            except BeltSurveySession.DoesNotExist:
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
                msg = _("No valid entries to add. Errors: ") + ", ".join(
                    survey_data.erros if survey_data else ["No data"]
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
                "message": _("No valid entries to add. Missing types: ")
                + ", ".join(missing_types)
                + ". Errors: "
                + ", ".join(survey_data.erros if survey_data else ["No data"]),
            }
