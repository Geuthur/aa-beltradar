# Standard Library
from typing import TYPE_CHECKING

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
from beltradar.providers import AppLogger, esi

if TYPE_CHECKING:
    # Alliance Auth
    from esi.stubs import MarketsPricesGetItem

    # AA Belt Radar
    from beltradar.models import BeltSurveyEntry as BeltSurveyEntryContext
    from beltradar.models import BeltSurveySession as BeltSurveyContext
    from beltradar.models import EveMarketPrice as EveTypePriceContext

logger = AppLogger(get_extension_logger(__name__), __title__)


class BeltRadarQuerySet(models.QuerySet["BeltSurveyContext"]):
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
            queries = [models.Q(eve_character__character_ownership__user=user)]

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
            query = models.Q(eve_character__character_ownership__user=user)
            logger.debug("Returning own survey sessions for User %s.", user)

            if query is None:
                return self.none()

            return self.filter(query)
        except AssertionError:
            logger.debug("User %s has no main character. Nothing visible.", user)
            return self.none()


class BeltRadarManager(models.Manager["BeltSurveyContext"]):
    def get_queryset(self) -> BeltRadarQuerySet:
        return BeltRadarQuerySet(self.model, using=self._db)

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


class BeltSurveyEntryQuerySet(models.QuerySet["BeltSurveyEntryContext"]):
    def for_snapshot(self, snapshot):
        """Filter entries for a specific snapshot."""
        return self.filter(snapshot=snapshot)

    def first_snapshot(self):
        """Get the earliest snapshot in this queryset."""
        return self.order_by("timestamp").values_list("snapshot", flat=True).first()

    def last_snapshot(self):
        """Get the most recent snapshot in this queryset."""
        return self.order_by("-timestamp").values_list("snapshot", flat=True).first()

    def snapshot_total_volume(self, snapshot):
        """Get the total volume_left for a specific snapshot."""
        return sum(
            entry.volume_left
            for entry in self.for_snapshot(snapshot).values_list(
                "volume_left", flat=True
            )
        )

    def snapshot_asteroid_count(self, snapshot):
        """Get the number of asteroids with volume > 0 for a specific snapshot."""
        return self.for_snapshot(snapshot).filter(volume_left__gt=0).count()


class BeltSurveyEntryManager(models.Manager["BeltSurveyEntryContext"]):
    def get_queryset(self) -> BeltSurveyEntryQuerySet:
        return BeltSurveyEntryQuerySet(self.model, using=self._db)

    def for_snapshot(self, snapshot):
        """Filter entries for a specific snapshot."""
        return self.get_queryset().for_snapshot(snapshot)

    def first_snapshot(self):
        """Get the earliest snapshot."""
        return self.get_queryset().first_snapshot()

    def snapshot_stats(self, snapshot):
        """Get aggregated stats for a snapshot. Returns a dict with total_volume and asteroid_count."""
        entries = self.for_snapshot(snapshot)
        return {
            "total_volume": sum(e.volume_left for e in entries),
            "asteroid_count": sum(1 for e in entries if e.volume_left > 0),
            "entry_count": entries.count(),
        }


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
