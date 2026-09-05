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
from beltradar.constants import ARRAY_ORE, ICE_ORE, NORMAL_ORE
from beltradar.helpers.eveonline import get_icon_render_url
from beltradar.models.helper.choices import BeltSizeChoice, BeltTypeChoice
from beltradar.providers import AppLogger, esi

if TYPE_CHECKING:
    # Alliance Auth
    from esi.stubs import MarketsPricesGetItem

    # AA Belt Radar
    from beltradar.models import BeltSurveyEntry as BeltSurveyEntryContext
    from beltradar.models import BeltSurveySession as SessionContext
    from beltradar.models import BeltSurveySnapshot as BeltSurveySnapshotContext
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
            queries.append(models.Q(is_public=True))

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

    def get_queryset(self) -> SessionQuerySet:
        return SessionQuerySet(self.model, using=self._db)


class BeltTimerQuerySet(AccessQuerySet["BeltTimerContext"]):
    """QuerySet with access control methods for Belt Timer model."""

    pass  # pylint: disable=unnecessary-pass


class BeltTimerManager(AccessManager["BeltTimerContext"]):
    """Manager with access control methods for Belt Timer model."""

    def get_queryset(self) -> BeltTimerQuerySet:
        return BeltTimerQuerySet(self.model, using=self._db)


class BeltSurveyEntryQuerySet(models.QuerySet["BeltSurveyEntryContext"]):
    pass


class BeltSurveyEntryManager(models.Manager["BeltSurveyEntryContext"]):
    pass


class BeltSurveySnapshotQuerySet(models.QuerySet["BeltSurveySnapshotContext"]):
    @staticmethod
    def _resolve_belt_size(volume_left, size_volumes):
        """Return the size whose documented total volume is closest."""
        return min(size_volumes, key=lambda size: abs(volume_left - size[0]))[1]

    @staticmethod
    def _contains_ore_variant(ore_names: set[str], ore_list: list[str]) -> bool:
        """Return whether names include a base ore or one of its named variants."""
        normalized_base_names = {ore_name.casefold() for ore_name in ore_list}
        return any(
            ore_name == base_name or ore_name.startswith(f"{base_name} ")
            for ore_name in ore_names
            for base_name in normalized_base_names
        )

    def previous_snapshot(self, snapshot: "BeltSurveySnapshotContext"):
        """Get previous snapshot relative to the given snapshot."""
        qs = self
        next_qs = qs.order_by("timestamp").exclude(pk=snapshot.pk)
        if not next_qs:
            return None
        return next_qs.first()

    def rate_per_s(self, first_snapshot=None, second_snapshot=None):
        """Calculate the mining rate between two snapshots."""
        if first_snapshot is None:
            first_snapshot = self.order_by("timestamp").first()
        if second_snapshot is None:
            second_snapshot = self.order_by("-timestamp").first()

        if first_snapshot is None or second_snapshot is None:
            return 0.0

        duration = (
            second_snapshot.timestamp - first_snapshot.timestamp
        ).total_seconds()
        if duration <= 0:
            return 0.0

        mined_m3 = first_snapshot.belt_size_m3 - second_snapshot.belt_size_m3
        if mined_m3 <= 0:
            return 0.0
        return round(mined_m3 / duration, 2)

    def belt_size_m3(self):
        """Get the total volume_left for all entries in this queryset."""
        belt_size = self.aggregate(total_volume=models.Sum("asteroids__volume_left"))[
            "total_volume"
        ]
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

    def rate_per_s_for_snapshot(self, snapshot: "BeltSurveySnapshotContext"):
        """Calculate the mining rate in m3/s for a specific snapshot."""
        previous_snapshot = self.previous_snapshot(snapshot)
        if previous_snapshot is None:
            return 0.0
        return self.rate_per_s(
            first_snapshot=previous_snapshot, second_snapshot=snapshot
        )

    def session_progress_percentage(
        self,
        asteroids: "BeltSurveyEntryQuerySet",
        remaining_asteroids: "BeltSurveyEntryQuerySet",
    ):
        """Calculate the progress percentage of the belt survey."""
        initial_volume = (
            asteroids.aggregate(models.Sum("volume_left"))["volume_left__sum"] or 0
        )
        current_volume = (
            remaining_asteroids.aggregate(models.Sum("volume_left"))["volume_left__sum"]
            or 0
        )

        if initial_volume <= 0:
            return 0.0

        progress_percentage = ((initial_volume - current_volume) / initial_volume) * 100
        return progress_percentage

    def session_finish_eta(
        self,
        asteroids: "BeltSurveyEntryQuerySet",
        remaining_asteroids: "BeltSurveyEntryQuerySet",
    ):
        """Estimate the finish time based on session entries."""
        # Calculate the duration between the two snapshots
        duration = (
            remaining_asteroids.first().snapshot.timestamp
            - asteroids.first().snapshot.timestamp
        ).total_seconds()

        # If the duration is zero or negative, return None to avoid division by zero
        if duration <= 0:
            return None

        # Calculate the mined volume between the two snapshots
        mined_m3 = (
            asteroids.aggregate(models.Sum("volume_left"))["volume_left__sum"] or 0
        ) - (
            remaining_asteroids.aggregate(models.Sum("volume_left"))["volume_left__sum"]
            or 0
        )
        if mined_m3 <= 0:
            return None

        # Calculate the mining rate in m3/s and estimate the finish time
        rate_m3 = mined_m3 / duration
        eta_seconds = (
            remaining_asteroids.aggregate(models.Sum("volume_left"))["volume_left__sum"]
            or 0
        ) / rate_m3

        # If the estimated time is less than or equal to zero, return None
        if eta_seconds <= 0:
            return None

        return remaining_asteroids.first().snapshot.timestamp + timezone.timedelta(
            seconds=eta_seconds
        )

    # pylint: disable=too-many-return-statements
    def session_resolve_belt(self) -> tuple[BeltTypeChoice, BeltSizeChoice] | None:
        """Resolve the belt type based on the first snapshot entries."""
        asteroids = self.filter(asteroids__volume_left__gt=0)
        ore_names = set(asteroids.values_list("asteroids__eve_type__name", flat=True))
        if not ore_names:
            return (None, None)

        ore_names = {ore_name.casefold() for ore_name in ore_names}
        volume_left = asteroids.belt_size_m3()
        print(volume_left)

        # Check for Ice ores
        if self._contains_ore_variant(ore_names, ICE_ORE):
            return BeltTypeChoice.ICE_BELT, BeltSizeChoice.ICE

        # Check for Array ores
        if self._contains_ore_variant(ore_names, ARRAY_ORE):
            return (
                BeltTypeChoice.ARRAY_BELT,
                self._resolve_belt_size(
                    volume_left,
                    (
                        (1_000_000, BeltSizeChoice.SMALL),
                        (4_000_000, BeltSizeChoice.MEDIUM),
                        (10_000_000, BeltSizeChoice.LARGE),
                    ),
                ),
            )

        # Check for Mercoxit ores
        if any(ore_name.startswith("mercoxit") for ore_name in ore_names):
            return (
                BeltTypeChoice.MERCOXIT_BELT,
                self._resolve_belt_size(
                    volume_left,
                    (
                        (10_000, BeltSizeChoice.SMALL),
                        (40_000, BeltSizeChoice.MEDIUM),
                        (240_000, BeltSizeChoice.LARGE),
                        (960_000, BeltSizeChoice.ENORMOUS),
                    ),
                ),
            )

        # Check for Normal ores
        if self._contains_ore_variant(ore_names, NORMAL_ORE):
            return (
                BeltTypeChoice.ASTEROID_BELT,
                self._resolve_belt_size(
                    volume_left,
                    (
                        (340_000, BeltSizeChoice.SMALL),
                        (1_180_000, BeltSizeChoice.MEDIUM),
                        (1_880_000, BeltSizeChoice.LARGE),
                        (3_210_000, BeltSizeChoice.ENORMOUS),
                        (3_900_000, BeltSizeChoice.COLOSSAL),
                    ),
                ),
            )
        return (None, None)


class BeltSurveySnapshotManager(models.Manager["BeltSurveySnapshotContext"]):
    def get_queryset(self) -> BeltSurveySnapshotQuerySet:
        return BeltSurveySnapshotQuerySet(self.model, using=self._db)

    def previous_snapshot(self, snapshot: "BeltSurveySnapshotContext"):
        """Get the snapshot immediately before the given snapshot."""
        return self.get_queryset().previous_snapshot(snapshot)

    def rate_per_s(
        self,
        first_snapshot: "BeltSurveySnapshotContext" = None,
        second_snapshot: "BeltSurveySnapshotContext" = None,
    ):
        """Calculate the mining rate in m3/s between two snapshots."""
        return self.get_queryset().rate_per_s(
            first_snapshot=first_snapshot, second_snapshot=second_snapshot
        )

    def rate_per_s_for_snapshot(self, snapshot: "BeltSurveySnapshotContext"):
        """Calculate the mining rate in m3/s for a specific snapshot."""
        return self.get_queryset().rate_per_s_for_snapshot(snapshot=snapshot)

    def session_progress_percentage(
        self,
        asteroids: "BeltSurveyEntryQuerySet",
        remaining_asteroids: "BeltSurveyEntryQuerySet",
    ):
        """Calculate the progress percentage of the belt survey."""
        return self.get_queryset().session_progress_percentage(
            asteroids, remaining_asteroids
        )

    def session_finish_eta(
        self,
        asteroids: "BeltSurveyEntryQuerySet",
        remaining_asteroids: "BeltSurveyEntryQuerySet",
    ) -> float | None:
        """Estimate the finish time based on the last two entries."""
        return self.get_queryset().session_finish_eta(
            asteroids=asteroids, remaining_asteroids=remaining_asteroids
        )

    def session_resolve_belt(self) -> tuple[BeltTypeChoice, BeltSizeChoice] | None:
        """Resolve the belt type based on the last snapshot entries."""
        return self.get_queryset().session_resolve_belt()

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
