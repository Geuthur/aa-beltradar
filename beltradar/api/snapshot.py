# Standard Library
import json
from http import HTTPStatus

# Third Party
from ninja import NinjaAPI

# Django
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone
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
    get_session_or_none,
)
from beltradar.api.helpers.icons import (
    get_snapshot_delete_button,
)
from beltradar.models.beltradar import (
    BeltSurveyEntry,
    BeltSurveySession,
    BeltSurveySnapshot,
    EveMarketPrice,
    generate_unique_public_id,
)
from beltradar.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


class BeltRadarApiEndpoints:
    tags = ["Survey"]

    # pylint: disable=too-many-statements
    def __init__(self, api: NinjaAPI):
        @api.get(
            "view/session/{public_id}/snapshot/last_snapshot/",
            response={
                HTTPStatus.OK: schema.SnapShotSchema,
                HTTPStatus.FORBIDDEN: dict,
                HTTPStatus.NOT_FOUND: schema.SnapShotSchema,
            },
            tags=self.tags,
        )
        def get_snapshot(request, public_id: str):
            """
            Get the last snapshot for the given session.

            Args:
                public_id (str): The public ID of the survey session.
            Returns:
                200: The last snapshot for the given session in the API response format.
                403: An error message if the user does not have permission to access the survey session.
                404: An error message if the survey session is not found.
            """
            # pylint: disable=duplicate-code
            if not request.user.has_perm("beltradar.basic_access"):
                return HTTPStatus.FORBIDDEN, {"error": _("Permission Denied.")}

            # Check if the survey session exists
            try:
                session = BeltSurveySession.objects.get(public_id=public_id)
            except ObjectDoesNotExist:
                return HTTPStatus.NOT_FOUND, {
                    "error": _("Belt Session not found or not public.")
                }

            snapshot = session.br_snapshots.order_by("-timestamp").first()
            if not snapshot:
                return HTTPStatus.NOT_FOUND, schema.SnapShotSchema()

            # Aggregate data for the last snapshot
            aggregated_items = session.br_snapshots.aggregate_entries_by_ore(
                entries=snapshot.asteroids.all()
            )

            # Create a list of survey entries for the current user, ordered by timestamp
            ore_list: list[schema.OreSchema] = []
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
                )
                ore_list.append(ore_data)

            return HTTPStatus.OK, schema.SnapShotSchema(
                snapshot=schema.SnapShotDataSchema(
                    identifier=snapshot.identifier,
                    first_timestamp=session.first_timestamp,
                    last_timestamp=session.last_timestamp,
                ),
                ore_list=ore_list,
                charts=generate_apex_chart_mining_data(session=session),
                traffic=generate_apex_chart_traffic_data(session=session),
                actions=schema.ActionSchema(
                    delete=get_snapshot_delete_button(
                        request=request,
                        public_id=session.public_id,
                        identifier=snapshot.identifier,
                    ),
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
            msg = _("Survey session and all associated entries deleted successfully.")
            return HTTPStatus.OK, {"success": True, "message": msg}

        @api.post(
            "manage/delete-snapshot/{public_id}/snapshot/{identifier}/",
            response={
                HTTPStatus.OK: dict,
                HTTPStatus.FORBIDDEN: dict,
                HTTPStatus.NOT_FOUND: dict,
            },
            tags=self.tags,
        )
        def delete_snapshot(request, public_id: str, identifier: str):
            """
            Delete all survey entries for a specific snapshot in a survey session.

            This Endpoint allows users to delete all entries associated with a specific snapshot timestamp within a survey session.
            The user must have permission to delete the survey session, and the survey session must exist.

            Args:
                public_id (str): The public UUID of the survey session.
                identifier (str): The identifier of the snapshot to delete.
            Returns:
                200: A success message indicating the snapshot was deleted.
                403: An error message if the user does not have permission or the session is not found.
                404: An error message if no entries are found for the given snapshot.
            """
            # Check if the user has permission to delete this snapshot (by checking if they can delete the survey session)
            perms, session = get_session_or_none(
                request=request,
                public_id=public_id,
            )

            # pylint: disable=duplicate-code
            if perms is False:
                return HTTPStatus.FORBIDDEN, {"error": _("Permission Denied.")}
            # pylint: disable=duplicate-code
            if perms is None:
                return HTTPStatus.NOT_FOUND, {
                    "error": _("Requested resource not found.")
                }

            deleted_count = session.br_snapshots.filter(identifier=identifier).delete()[
                0
            ]
            if deleted_count == 0:
                msg = _("No entries found for the given snapshot.")
                return HTTPStatus.NOT_FOUND, {"error": msg}

            # If entries were deleted successfully, return a success message
            msg = _("Snapshot deleted successfully.")
            return HTTPStatus.OK, {"success": True, "message": msg}

        # pylint: disable=too-many-branches, too-many-return-statements
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
        def add_snapshot(request, public_id: str):  # pylint: disable=too-many-locals
            """
            Add a snapshot to a session.

            This Endpoint allows users to add a new snapshot to an existing session.
            The user must have permission to add snapshots to the session, and the session must exist.

            Args:
                public_id (str): The public UUID of the session.
                parsed_data: A JSON object containing the snapshot data, including ore name, units, volume, price, timestamp, and snapshot identifier.
            Returns:
                200: A success message indicating the snapshot was added.
                400: An error message if the input data is invalid or cannot be parsed.
                403: An error message if the user does not have permission or the session is not found.
                404: An error message if the session is not found.
            """
            # Check if the user has permission to add snapshots to this session
            perms, session = get_session_or_none(
                request=request,
                public_id=public_id,
            )
            # pylint: disable=duplicate-code
            if perms is False:
                return HTTPStatus.FORBIDDEN, {"error": _("Permission Denied.")}
            # pylint: disable=duplicate-code
            if perms is None:
                return HTTPStatus.NOT_FOUND, {
                    "error": _("Requested resource not found.")
                }

            # Validate the form data
            form = forms.AddSnapshotForm(data=json.loads(request.body))
            if not form.is_valid():
                try:
                    msg = form.errors.as_json(escape_html=False)
                except IndexError:
                    msg = _(
                        "Invalid input data. Please check the format and try again."
                    )
                return HTTPStatus.BAD_REQUEST, {"success": False, "message": msg}

            snapshot_asteroids = []
            snapshot_data: schema.OreSchemaResponse = form.cleaned_data.get(
                "raw_data", None
            )

            # If no valid entries were parsed from the input data, return an error message
            if not snapshot_data or not snapshot_data.ore_list:
                msg = _("No valid entries to add. Errors:") + " , ".join(
                    snapshot_data.errors if snapshot_data else ["No data"]
                )
                return HTTPStatus.BAD_REQUEST, {"success": False, "message": msg}

            missing_types = []
            names = [item.name for item in snapshot_data.ore_list]
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

            for item in snapshot_data.ore_list:
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

                snapshot_asteroids.append(
                    {
                        "eve_type_id": eve_type_id,
                        "units": item.units,
                        "volume_left": item.volume_m3,
                        "price": price,
                        "price_compressed": compressed_price,
                        "note": (
                            f"Added via batch import. Missing types: {', '.join(missing_types)}"
                            if missing_types
                            else "Added via batch import."
                        ),
                    }
                )

            if snapshot_asteroids:
                with transaction.atomic():
                    snapshot = BeltSurveySnapshot.objects.create(
                        session=session,
                        recorded_by=request.user,
                        timestamp=timezone.now(),
                        identifier=generate_unique_public_id(length=12),
                    )
                    snapshot_asteroids = [
                        BeltSurveyEntry(snapshot=snapshot, **entry_data)
                        for entry_data in snapshot_asteroids
                    ]
                    BeltSurveyEntry.objects.bulk_create(snapshot_asteroids)
                    snapshot.asteroids.set(snapshot_asteroids)
                    if not session.br_belt_timer.exists():
                        # Try to create a Belt Timer after the snapshot is complete.
                        session.create_belt_timer()
                return HTTPStatus.OK, {
                    "success": True,
                    "message": _("Survey entry added successfully."),
                }
            return HTTPStatus.BAD_REQUEST, {
                "success": False,
                "message": _("No valid entries to add. Missing types:")
                + " , ".join(missing_types)
                + ". Errors: "
                + ", ".join(snapshot_data.errors if snapshot_data else ["No data"]),
            }
