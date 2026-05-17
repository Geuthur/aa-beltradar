# Standard Library
from collections import defaultdict

# Third Party
from ninja import NinjaAPI

# Django
from django.db.models import QuerySet
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
from beltradar.models.beltradar import BeltSurveyEntry, BeltSurveySession
from beltradar.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


class BeltRadarSurveyApiEndpoints:
    tags = ["Survey"]

    # pylint: disable=too-many-locals
    def ore_mining_stats(
        self,
        entries: QuerySet[BeltSurveyEntry],
    ) -> schema.OreChartDataSchema:
        """Calculate per-ore mining progress from first to last snapshot."""
        ordered_entries = list(entries.select_related("eve_type").order_by("timestamp"))
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

        start_snapshot = ordered_snapshots[0]
        end_snapshot = ordered_snapshots[-1]
        previous_snapshot = ordered_snapshots[-2]

        start_map = dict(start_snapshot["ores"])
        end_map = dict(end_snapshot["ores"])
        previous_map = dict(previous_snapshot["ores"])

        start_ts = start_snapshot["timestamp"]
        end_ts = end_snapshot["timestamp"]
        prev_ts = previous_snapshot["timestamp"]

        total_duration_seconds = max(0.0, (end_ts - start_ts).total_seconds())
        last_step_seconds = max(0.0, (end_ts - prev_ts).total_seconds())

        ore_names = sorted(set(start_map.keys()) | set(end_map.keys()))
        categories: list[str] = []
        progress_data: list[float] = []
        items: list[schema.OreMiningChartItemSchema] = []

        for ore_name in ore_names:
            start_volume = max(0.0, float(start_map.get(ore_name, 0.0)))
            volume_left = max(0.0, float(end_map.get(ore_name, 0.0)))
            previous_volume = max(0.0, float(previous_map.get(ore_name, volume_left)))

            volume_mined = max(0.0, start_volume - volume_left)
            progress_percent = (
                min(100.0, max(0.0, (volume_mined / start_volume) * 100.0))
                if start_volume > 0
                else 0.0
            )

            rate_m3_per_s = 0.0
            if last_step_seconds > 0:
                step_mined = max(0.0, previous_volume - volume_left)
                rate_m3_per_s = step_mined / last_step_seconds
            elif total_duration_seconds > 0 and volume_mined > 0:
                rate_m3_per_s = volume_mined / total_duration_seconds

            eta_seconds = (volume_left / rate_m3_per_s) if rate_m3_per_s > 0 else None

            categories.append(ore_name)
            progress_data.append(round(progress_percent, 2))
            items.append(
                schema.OreMiningChartItemSchema(
                    ore_name=ore_name,
                    start_volume=round(start_volume, 2),
                    volume_left=round(volume_left, 2),
                    volume_mined=round(volume_mined, 2),
                    progress_percent=round(progress_percent, 2),
                    rate_m3_per_s=round(rate_m3_per_s, 4),
                    eta_seconds=(
                        round(eta_seconds, 2) if eta_seconds is not None else None
                    ),
                )
            )
        return schema.OreChartDataSchema(
            categories=categories,
            series=[
                schema.OreMiningChartSeriesSchema(
                    name="Mined %",
                    data=progress_data,
                )
            ],
            items=items,
        )

    def session_stats(self, session: BeltSurveySession) -> schema.SnapShotStatsSchema:
        """Calculate belt stats for the latest snapshot of the given survey session."""
        return schema.SnapShotStatsSchema(
            belt_volume=session.belt_size_m3,
            belt_volume_left_m3=session.belt_left_m3,
            remaining_asteroids=session.remaining_asteroids,
            total_asteroids=session.total_asteroids,
            progress_percent=round(session.progress_percent, 2),
            duration_seconds=round(session.duration_seconds, 2),
            mining_rate_m3_per_s=round(session.mining_rate_m3_per_s, 4),
            finish_eta=session.finish_eta,
        )

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
            "view/session/{public_id}/snapshot/last_entry/",
            response={200: schema.SnapShotSchema, 403: dict, 404: dict},
            tags=self.tags,
        )
        def get_survey_entry(request, public_id: str):
            """Get all survey entries for the current user."""
            if not request.user.has_perm("beltradar.basic_access"):
                return 403, {
                    "error": _("You do not have permission to access this resource.")
                }

            # Check if the survey session exists
            session = BeltSurveySession.objects.filter(public_id=public_id).first()
            if not session:
                return 404, {"error": _("Survey session not found or not public.")}

            # Get the most recent survey entry for this session (if any)
            entries = session.br_entries.select_related("eve_type")
            last_entries = entries.order_by("-timestamp").filter(
                snapshot=session.last_entry_snapshot()
            )

            if not last_entries:
                return 404, {"error": _("No survey entries found for this session.")}

            # Create a list of survey entries for the current user, ordered by timestamp
            snapshot_list: list[schema.OreSchema] = []
            for entry in last_entries:
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

            return 200, schema.SnapShotSchema(
                snapshot=last_entries[0].snapshot,
                timestamp=last_entries[0].timestamp,
                entries=snapshot_list,
                charts=self.ore_mining_stats(entries=entries),
                stats=self.session_stats(session=session),
                session_name=session.name,
                session_created_at=session.created_at,
                session_owner=str(session.owner),
                delete_html=str(
                    get_snapshot_delete_button(
                        request=request,
                        public_id=session.public_id,
                        snapshot=session.last_entry_snapshot(),
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
