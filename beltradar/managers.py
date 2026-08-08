# Standard Library
from typing import TYPE_CHECKING, Generic, TypeVar

# Django
from django.db import models
from django.utils import timezone

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from eve_sde.models import ItemType

# AA Belt Radar
from beltradar import __title__
from beltradar.app_settings import BELT_RADAR_BULK_BATCH_SIZE
from beltradar.helpers.eveonline import get_icon_render_url
from beltradar.providers import AppLogger, esi

if TYPE_CHECKING:
    # Alliance Auth
    from esi.stubs import MarketsPricesGetItem

    # AA Belt Radar
    from beltradar.models import BeltSurveyEntry as BeltSurveyEntryContext
    from beltradar.models import BeltSurveySession as SessionContext
    from beltradar.models import BeltTimer as BeltTimerContext
    from beltradar.models import EveMarketPrice as EveTypePriceContext

logger = AppLogger(get_extension_logger(__name__), __title__)

T = TypeVar("T", bound=models.Model)


class AccessQuerySet(models.QuerySet[T], Generic[T]):
    """QuerySet with access control methods for Belt Radar models."""

    def visible_to(self, user):
        """Get all survey sessions visible to the user."""
        # superusers get all visible
        if user.is_superuser:
            logger.debug(
                "Returning all survey sessions for superuser %s.",
                user,
            )
            return self

        if user.has_perm("taxsystem.admin_access"):
            logger.debug("Returning all survey sessions for admin user %s.", user)
            return self

        try:
            char = user.profile.main_character
            assert char
            queries = [models.Q(owner=user)]

            logger.debug(
                "%s queries for user %s visible survey sessions.", len(queries), user
            )

            query = queries.pop()
            for q in queries:
                query |= q
            return self.filter(query)
        except AssertionError:
            logger.debug("User %s has no main character. Nothing visible.", user)
            return self.none()

    def manage_to(self, user):
        """Get all survey sessions that the user can manage."""
        # superusers get all visible
        if user.is_superuser:
            logger.debug(
                "Returning all survey sessions for superuser %s.",
                user,
            )
            return self

        if user.has_perm("taxsystem.admin_access"):
            logger.debug("Returning all survey sessions for admin user %s.", user)
            return self

        try:
            char = user.profile.main_character
            assert char
            query = models.Q(owner=user)
            logger.debug("Returning own survey sessions for User %s.", user)

            if query is None:
                return self.none()

            return self.filter(query)
        except AssertionError:
            logger.debug("User %s has no main character. Nothing visible.", user)
            return self.none()


class AccessManager(models.Manager[T], Generic[T]):
    """Manager with access control methods for Belt Radar models."""

    def get_queryset(self) -> AccessQuerySet[T]:
        return AccessQuerySet(self.model, using=self._db)

    def visible_to(self, user):
        return self.get_queryset().visible_to(user)

    def manage_to(self, user):
        return self.get_queryset().manage_to(user)

    @staticmethod
    def visible_eve_characters(user):
        qs = EveCharacter.objects.get_queryset()
        if user.is_superuser:
            logger.debug("Returning all characters for superuser %s.", user)
            return qs.all()

        if user.has_perm("beltradar.admin_access"):
            logger.debug("Returning all characters for %s.", user)
            return qs.all()

        try:
            char = user.profile.main_character
            assert char
            queries = [models.Q(character_ownership__user=user)]

            logger.debug(
                "%s queries for user %s visible chracters.", len(queries), user
            )

            query = queries.pop()
            for q in queries:
                query |= q
            return qs.filter(query)
        except AssertionError:
            logger.debug("User %s has no main character. Nothing visible.", user)
            return qs.none()


class SessionQuerySet(AccessQuerySet["SessionContext"]):
    """QuerySet with access control methods for Belt Survey Session model."""

    pass  # pylint: disable=unnecessary-pass


class SessionManager(AccessManager["SessionContext"]):
    """Manager with access control methods for Belt Survey Session model."""

    pass  # pylint: disable=unnecessary-pass


class BeltSurveyEntryQuerySet(models.QuerySet["BeltSurveyEntryContext"]):
    def for_snapshot(self, snapshot: str):
        """Filter entries for a specific snapshot."""
        if snapshot is None:
            return self.none()
        return self.filter(snapshot=snapshot)

    def previous_snapshot(self, snapshot: str):
        """Get the snapshot immediately before the given snapshot."""
        target_timestamp = (
            self.filter(snapshot=snapshot)
            .order_by("timestamp")
            .values_list("timestamp", flat=True)
            .first()
        )
        if target_timestamp is None:
            return None

        return (
            self.filter(timestamp__lt=target_timestamp)
            .order_by("-timestamp")
            .values_list("snapshot", flat=True)
            .first()
        )

    def snapshots(self):
        """Get all snapshots in this queryset."""
        return self.values_list("snapshot", flat=True).order_by("timestamp").distinct()

    def snapshot_entries(self) -> list[list["BeltSurveyEntryContext"]]:
        """Get all entries grouped by snapshot."""
        snapshots = self.snapshots()
        snapshot_entries = []
        for snapshot in snapshots:
            snapshot_entries.append(self.for_snapshot(snapshot))
        return snapshot_entries

    def belt_size_m3(self):
        """Get the total volume_left for all entries in this queryset."""
        belt_size = self.aggregate(total_volume=models.Sum("volume_left"))[
            "total_volume"
        ]
        return float(belt_size) if belt_size is not None else 0.0

    def belt_size_m3_for_snapshot(self, snapshot: str):
        """Get the total volume_left for a specific snapshot."""
        belt_size = self.filter(snapshot=snapshot).aggregate(
            total_volume=models.Sum("volume_left")
        )["total_volume"]
        return float(belt_size) if belt_size is not None else 0.0

    def duration(
        self,
        first_entry: "BeltSurveyEntryContext",
        last_entry: "BeltSurveyEntryContext",
    ):
        """Calculate the duration in seconds for this queryset."""
        if first_entry is None:
            return 0.0
        if last_entry is None:
            return 0.0
        return (last_entry.timestamp - first_entry.timestamp).total_seconds()

    def rate_per_s(
        self,
        first_entries: "BeltSurveyEntryQuerySet" = None,
        second_entries: "BeltSurveyEntryQuerySet" = None,
    ):
        """Calculate the mining rate in m3/s based on the last two snapshots."""
        snapshots = self.snapshots()

        # If there are less than 2 snapshots, we cannot calculate progress percentage
        if not snapshots or snapshots.count() < 2:
            return 0.0

        # If first_entries or second_entries are not provided, get the entries for the first and last snapshots
        if first_entries is None or second_entries is None:
            first_entries = self.for_snapshot(snapshots.first())
            second_entries = self.for_snapshot(snapshots.last())

        # Calculate the duration between the two snapshots
        duration = (
            second_entries.last().timestamp - first_entries.last().timestamp
        ).total_seconds()

        # If the duration is zero or negative, return 0.0 to avoid division by zero
        if duration <= 0:
            return 0.0

        # Calculate the mined volume between the two snapshots
        mined_m3 = first_entries.belt_size_m3() - second_entries.belt_size_m3()

        # If the mined volume is zero or negative, return 0.0 to avoid negative rates
        if mined_m3 <= 0:
            return 0.0
        return round(mined_m3 / duration, 2)

    def rate_per_s_for_snapshot(self, snapshot: str):
        """Calculate the mining rate in m3/s for a specific snapshot."""
        previous_snapshot = self.previous_snapshot(snapshot)
        if previous_snapshot is None:
            return 0.0

        first_entries = self.for_snapshot(previous_snapshot)
        second_entries = self.for_snapshot(snapshot)

        return self.rate_per_s(first_entries, second_entries)

    def timestamp_for_snapshot(self, snapshot: str):
        """Get the timestamp for a specific snapshot."""
        entry = self.filter(snapshot=snapshot).order_by("timestamp").first()
        return entry.timestamp if entry else None

    def asteroid_count(self):
        """Get the number of asteroids with volume > 0."""
        return self.filter(volume_left__gt=0).count()

    def session_progress_percentage(self):
        """Calculate the progress percentage of the belt survey."""
        snapshots = self.snapshots()

        # If there are less than 2 snapshots, we cannot calculate progress percentage
        if not snapshots or snapshots.count() < 2:
            return 0.0

        p_entries = self.for_snapshot(snapshots.first())
        l_entries = self.for_snapshot(snapshots.last())

        # If either of the entry sets is empty, we cannot calculate the finish time
        if not p_entries.exists() or not l_entries.exists():
            return 0.0

        initial_volume = p_entries.belt_size_m3()
        current_volume = l_entries.belt_size_m3()

        if initial_volume <= 0:
            return 0.0

        progress_percentage = ((initial_volume - current_volume) / initial_volume) * 100
        return progress_percentage

    def session_finish_eta(self):
        """Estimate the finish time based on session entries."""
        snapshots = self.snapshots()

        # If there are less than 2 snapshots, we cannot calculate progress percentage
        if not snapshots or snapshots.count() < 2:
            return None

        # Get the entries for the last and previous snapshots
        p_entries = self.for_snapshot(self.previous_snapshot(snapshots.last()))
        l_entries = self.for_snapshot(snapshots.last())

        # If either of the entry sets is empty, we cannot calculate the finish time
        if not p_entries.exists() or not l_entries.exists():
            return None

        # Calculate the duration between the two snapshots
        duration = (
            l_entries.first().timestamp - p_entries.first().timestamp
        ).total_seconds()

        # If the duration is zero or negative, return None to avoid division by zero
        if duration <= 0:
            return None

        # Calculate the mined volume between the two snapshots
        mined_m3 = p_entries.belt_size_m3() - l_entries.belt_size_m3()
        if mined_m3 <= 0:
            return None

        # Calculate the mining rate in m3/s and estimate the finish time
        rate_m3 = mined_m3 / duration
        eta_seconds = l_entries.belt_size_m3() / rate_m3

        # If the estimated time is less than or equal to zero, return None
        if eta_seconds <= 0:
            return None

        return l_entries.first().timestamp + timezone.timedelta(seconds=eta_seconds)


class BeltSurveyEntryManager(models.Manager["BeltSurveyEntryContext"]):
    def get_or_create_respawn_timer(
        self, session: "SessionContext"
    ) -> "BeltTimerContext":
        """Get or Create a respawn timer for the given session."""
        pass  # pylint: disable=unnecessary-pass

    def get_queryset(self) -> BeltSurveyEntryQuerySet:
        return BeltSurveyEntryQuerySet(self.model, using=self._db)

    def for_snapshot(self, snapshot):
        """Filter entries for a specific snapshot."""
        return self.get_queryset().for_snapshot(snapshot)

    def previous_snapshot(self, snapshot):
        """Get the snapshot immediately before the given snapshot."""
        return self.get_queryset().previous_snapshot(snapshot)

    def snapshots(self):
        """Get all snapshots in this queryset."""
        return self.get_queryset().snapshots()

    def snapshot_entries(self):
        """Get all entries grouped by snapshot."""
        return self.get_queryset().snapshot_entries()

    def belt_size_m3(self):
        """Get the total volume_left for all entries."""
        return self.get_queryset().belt_size_m3()

    def belt_size_m3_for_snapshot(self, snapshot):
        """Get the total volume_left for a specific snapshot."""
        return self.get_queryset().belt_size_m3_for_snapshot(snapshot)

    def rate_per_s(self, first_entries=None, second_entries=None):
        """Calculate the mining rate in m3/s based on the last two snapshots."""
        return self.get_queryset().rate_per_s(first_entries, second_entries)

    def rate_per_s_for_snapshot(self, snapshot):
        """Calculate the mining rate in m3/s for a specific snapshot."""
        return self.get_queryset().rate_per_s_for_snapshot(snapshot)

    def duration(self, first_entry, last_entry):
        """Calculate the duration in seconds for this queryset."""
        return self.get_queryset().duration(first_entry, last_entry)

    def asteroid_count(self):
        """Get the number of asteroids with volume > 0."""
        return self.get_queryset().asteroid_count()

    def session_progress_percentage(self):
        """Calculate the progress percentage of the belt survey."""
        return self.get_queryset().session_progress_percentage()

    def session_finish_eta(self):
        """Estimate the finish time based on the last two entries."""
        return self.get_queryset().session_finish_eta()

    def snapshot_stats(self, snapshot):
        """Get aggregated stats for a snapshot. Returns a dict with total_volume and asteroid_count."""
        timestamp = self.get_queryset().timestamp_for_snapshot(snapshot)
        rate_per_s = self.get_queryset().rate_per_s_for_snapshot(snapshot)
        volume_left = self.get_queryset().belt_size_m3_for_snapshot(snapshot)

        return {
            "timestamp": timestamp,
            "rate_per_s": rate_per_s,
            "volume_left": volume_left,
        }

    def aggregate_entries_by_ore(
        self, entries: models.QuerySet["BeltSurveyEntryContext"]
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


class EveTypePriceQuerySet(models.QuerySet["EveTypePriceContext"]):
    pass


class EveMarketPriceManager(models.Manager["EveTypePriceContext"]):
    def get_queryset(self) -> EveTypePriceQuerySet:
        return EveTypePriceQuerySet(self.model, using=self._db)

    def update_from_esi(self) -> int:
        """Update or create EveMarketPrice from ESI data."""

        prices = self.fetch_data_from_esi()
        if not prices:
            logger.debug("No market price data fetched from ESI.")
            return 0

        updated_prices = self.update_objs_from_esi(prices)
        return updated_prices

    def fetch_data_from_esi(self) -> list["MarketsPricesGetItem"]:
        """Fetch market price data from ESI."""
        response = esi.client.Market.GetMarketsPrices().results(use_etag=False)
        return response

    def update_objs_from_esi(self, objs: list["MarketsPricesGetItem"]) -> int:
        """Update or create EveTypePrice objects from ESI data."""
        # pylint: disable=import-outside-toplevel
        # AA Belt Radar
        from beltradar.models import EveMarketPrice

        _update_price = []
        _new_price = []
        _esi_market_type_ids = {obj.type_id for obj in objs}
        _current_market_prices = {
            market_price.eve_type_id: market_price
            for market_price in EveMarketPrice.objects.filter(
                eve_type_id__in=_esi_market_type_ids
            )
        }
        _now = timezone.now()
        for obj in objs:
            if obj.type_id in _current_market_prices:
                eve_market_type = _current_market_prices[obj.type_id]
                eve_market_type.average_price = obj.average_price
                eve_market_type.adjusted_price = obj.adjusted_price
                eve_market_type.updated_at = _now
                _update_price.append(eve_market_type)
            else:
                eve_market_type = EveMarketPrice(
                    eve_type=ItemType.objects.get(
                        id=obj.type_id
                    ),  # TODO: optimize get? to avoid that much queries
                    average_price=obj.average_price,
                    adjusted_price=obj.adjusted_price,
                    updated_at=_now,
                )
                _new_price.append(eve_market_type)

        if _update_price:
            self.bulk_update(
                _update_price,
                fields=["average_price", "adjusted_price", "updated_at"],
                batch_size=BELT_RADAR_BULK_BATCH_SIZE,
            )
        if _new_price:
            self.bulk_create(
                _new_price, batch_size=BELT_RADAR_BULK_BATCH_SIZE, ignore_conflicts=True
            )
        return len(objs)
