"""Models for Belt Radar."""

# Standard Library
import uuid
from typing import TYPE_CHECKING

# Django
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.authentication.models import User
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from eve_sde.models import ItemType

# AA Belt Radar
from beltradar import __title__
from beltradar.managers import (
    BeltRadarManager,
    BeltSurveyEntryManager,
    EveMarketPriceManager,
)
from beltradar.models.helper.choices import BeltSizeChoice, BeltTypeChoice
from beltradar.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


def generate_unique_public_id(length=12):
    """Generate a unique public ID."""
    unique_id = str(uuid.uuid4())
    unique_id = unique_id.replace("-", "")
    return unique_id[:length]


class UserSettings(models.Model):
    class Meta:
        default_permissions = ()  # Remove standard permissions

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )

    disable_notifications = models.BooleanField(default=False)


class BeltSurveySession(models.Model):
    """Represents a single survey session for a belt, which can have multiple entries (BeltSurveyEntry)."""

    if TYPE_CHECKING:
        br_entries: BeltSurveyEntryManager
        br_timer: models.QuerySet["BeltTimer"]

    class Meta:
        default_permissions = ()  # Remove standard permissions

    objects: BeltRadarManager = BeltRadarManager()

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="br_user_sessions"
    )
    public_id = models.CharField(max_length=36, default="")
    name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """
        Override the save method to automatically generate a unique public_id before saving the BeltSurveySession instance.
        This ensures that each session has a unique identifier that can be used for public access or sharing.
        """
        # Generate a unique public_id if it is not already set
        if self.public_id == "":
            self.public_id = generate_unique_public_id()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.public_id})"

    def get_entries_for_snapshot(self, snapshot):
        """Get all entries for a specific snapshot. This is the preferred method for accessing snapshot data."""
        return self.br_entries.for_snapshot(snapshot)

    def first_entry(self):
        """Get the earliest survey entry in this session, or None if there are no entries."""
        return self.br_entries.order_by("timestamp").first()

    @cached_property
    def first_entry_snapshot(self):
        """Get the snapshot identifier of the earliest entry in this session, or None if there are no entries."""
        return (
            self.br_entries.order_by("timestamp")
            .values_list("snapshot", flat=True)
            .first()
        )

    @cached_property
    def first_entry_timestamp(self):
        """Get the timestamp of the earliest entry in this session, or None if there are no entries."""
        return (
            self.br_entries.order_by("timestamp")
            .values_list("timestamp", flat=True)
            .first()
        )

    def last_entry(self):
        """Get the most recent survey entry in this session, or None if there are no entries."""
        return self.br_entries.order_by("-timestamp").first()

    @cached_property
    def last_entry_snapshot(self):
        """Get the snapshot identifier of the most recent entry in this session, or None if there are no entries."""
        return (
            self.br_entries.order_by("-timestamp")
            .values_list("snapshot", flat=True)
            .first()
        )

    @cached_property
    def last_entry_timestamp(self):
        """Get the timestamp of the most recent entry in this session, or None if there are no entries."""
        return (
            self.br_entries.order_by("-timestamp")
            .values_list("timestamp", flat=True)
            .first()
        )

    @cached_property
    def previous_entry_snapshot(self):
        """Get the snapshot identifier of the entry before the most recent one in this session, or None if there are no previous entries."""
        snapshot = self.last_entry_snapshot
        if not snapshot:
            return None
        previous_entry = (
            self.br_entries.exclude(snapshot=snapshot).order_by("-timestamp").first()
        )
        if not previous_entry:
            return None
        return previous_entry.snapshot

    @property
    def belt_size_m3(self):
        """Calculate the total size of the belt in m3."""
        if not self.first_entry_snapshot:
            return 0
        entries = self.get_entries_for_snapshot(self.first_entry_snapshot)
        return sum(entry.volume_left for entry in entries)

    @property
    def belt_left_m3(self):
        """Calculate the volume left in the belt from the most recent snapshot."""
        if not self.last_entry_snapshot:
            return 0
        entries = self.get_entries_for_snapshot(self.last_entry_snapshot)
        return sum(entry.volume_left for entry in entries)

    @property
    def remaining_asteroids(self):
        """Calculate the number of remaining asteroids in the most recent snapshot."""
        if not self.last_entry_snapshot:
            return 0
        entries = self.get_entries_for_snapshot(self.last_entry_snapshot)
        return sum(1 for entry in entries if entry.volume_left > 0)

    @property
    def total_asteroids(self):
        """Calculate the total number of asteroids in the belt."""
        if not self.first_entry_snapshot:
            return 0
        entries = self.get_entries_for_snapshot(self.first_entry_snapshot)
        return sum(1 for entry in entries if entry.units > 0)

    @property
    def progress_percent(self):
        """Calculate the percentage of the belt that has been mined."""
        size = float(self.belt_size_m3)
        if size == 0:
            return 0.0
        left = float(self.belt_left_m3)
        mined = size - left
        return (mined / size) * 100.0

    @property
    def previous_entry_duration(self):
        """Calculate the duration between the last two snapshots in seconds."""
        last = self.last_entry()
        previous_snapshot = self.previous_entry_snapshot
        if not last or not previous_snapshot:
            return 0.0
        previous_entries = self.get_entries_for_snapshot(previous_snapshot)
        if not previous_entries:
            return 0.0
        previous = max(previous_entries, key=lambda e: e.timestamp)
        return (last.timestamp - previous.timestamp).total_seconds()

    @property
    def mining_rate_m3_per_s(self):
        """Calculate mining speed in m3/s."""
        duration = self.previous_entry_duration
        previous_snapshot = self.previous_entry_snapshot
        if not previous_snapshot or duration <= 0:
            return 0.0
        previous_entries = self.get_entries_for_snapshot(previous_snapshot)
        if not previous_entries:
            return 0.0
        previous_left_m3 = sum(entry.volume_left for entry in previous_entries)
        mined_m3 = previous_left_m3 - self.belt_left_m3
        return mined_m3 / duration

    @property
    def finish_eta(self):
        """Calculate the estimated time of completion for mining the belt."""
        rate = float(self.mining_rate_m3_per_s)
        if rate <= 0:
            return None
        left = float(self.belt_left_m3)
        eta_seconds = left / rate
        try:
            return self.last_entry().timestamp + timezone.timedelta(seconds=eta_seconds)
        except (OverflowError, OSError):
            return None

    @property
    def is_fresh(self):
        last = self.last_entry()
        if not last:
            return False
        age_seconds = (timezone.now() - last.timestamp).total_seconds()
        return (
            age_seconds < 300
        )  # consider fresh if last entry is less than 5 minutes old


class BeltSurveyEntry(models.Model):
    """Represents a single survey entry for a belt, linked to a BeltSurveySession."""

    objects: BeltSurveyEntryManager = BeltSurveyEntryManager()

    class Meta:
        default_permissions = ()  # Remove standard permissions
        ordering = ["timestamp"]

    session = models.ForeignKey(
        BeltSurveySession, on_delete=models.CASCADE, related_name="br_entries"
    )
    snapshot = models.CharField(max_length=64, null=True, blank=True)
    recorded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    timestamp = models.DateTimeField(default=timezone.now)
    eve_type = models.ForeignKey(
        ItemType, on_delete=models.CASCADE, related_name="br_survey_entries"
    )
    units = models.IntegerField(null=True, blank=True)
    volume_left = models.FloatField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    price_compressed = models.FloatField(null=True, blank=True)
    price = models.FloatField(null=True, blank=True)

    @property
    def income_per_h(self):
        """
        Calculate the estimated income in ISK per hour based on the current volume left and price.

        This calculation is based on the current price and the mining rate in m3/s.
        Formula: income per hour = price per m3 * mining rate in m3/s

        Returns:
            float: The estimated income in ISK per hour based on the price.
        """
        return self.price_per_m3 * self.session.mining_rate_m3_per_s

    @property
    def income_cmp_per_h(self):
        """
        Calculate the estimated income in ISK per hour based on the current volume left and compressed price.

        This calculation is based on the compressed price, which is typically for 100 units of the item, and the mining rate in m3/s.
        Formula: income per hour = compressed price per m3 * mining rate in m3/s

        Returns:
            float: The estimated income in ISK per hour based on the compressed price.
        """
        return self.price_cmp_per_m3 * self.session.mining_rate_m3_per_s

    @property
    def price_per_m3(self):
        """
        Calculate the price per m3 based on the current price and volume left.

        Formula: price per m3 = price / volume of one unit in m3

        Returns:
            float: The price per m3 based on the current price.
        """
        if not self.price or not self.volume_left:
            return 0
        return self.price / self.eve_type.volume

    @property
    def price_cmp_per_m3(self):
        """
        Calculate the compressed price per m3 based on the current compressed price and volume left.

        Formula: compressed price per m3 = price_compressed / (volume of one unit in m3 / 100)
        The division by 100 is because the compressed price is typically for 100 units of the item.

        Returns:
            float: The compressed price per m3 based on the current compressed price.
        """
        if not self.price_compressed or not self.volume_left:
            return 0
        return self.price_compressed / (self.eve_type.volume / 100)


class BeltTimer(models.Model):
    """Represents a timer for a belt, which can be used to track when the belt will be depleted."""

    class Meta:
        default_permissions = ()  # Remove standard permissions

    objects: BeltRadarManager = BeltRadarManager()

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="br_user_timers"
    )
    public_id = models.CharField(max_length=36, default="")
    belt_id = models.CharField(max_length=7)
    belt_name = models.CharField(max_length=100)
    belt_size = models.CharField(choices=BeltSizeChoice.choices, max_length=10)
    belt_type = models.CharField(choices=BeltTypeChoice.choices, max_length=15)
    eta = models.DateTimeField(null=True, blank=True)

    # Belt Timer visibility
    public = models.BooleanField(default=False)

    # Notification System
    sent_notification = models.BooleanField(default=False)

    # pylint: disable=too-many-branches
    def generate_eta(self):
        """Generate the estimated time of respawn for the belt based on belt type and current time."""
        now = timezone.now()
        # Basic belt respawn times (https://wiki.eveuniversity.org/Asteroids_and_ore#Ore_Prospecting_Arrays)
        if self.belt_type == BeltTypeChoice.ASTEROID_BELT:
            if self.belt_size == BeltSizeChoice.SMALL:
                self.eta = now + timezone.timedelta(hours=1)
            elif self.belt_size == BeltSizeChoice.MEDIUM:
                self.eta = now + timezone.timedelta(hours=2)
            elif self.belt_size == BeltSizeChoice.LARGE:
                self.eta = now + timezone.timedelta(hours=3)
            elif self.belt_size == BeltSizeChoice.ENORMOUS:
                self.eta = now + timezone.timedelta(hours=4)
            elif self.belt_size == BeltSizeChoice.COLOSSAL:
                self.eta = now + timezone.timedelta(hours=5)
        # Arrey belts have a different respawn time based on their size (https://wiki.eveuniversity.org/Asteroids_and_ore#Ore_Prospecting_Arrays)
        if self.belt_type == BeltTypeChoice.ARREY_BELT:
            if self.belt_size == BeltSizeChoice.SMALL:
                self.eta = now + timezone.timedelta(hours=1)
            elif self.belt_size == BeltSizeChoice.MEDIUM:
                self.eta = now + timezone.timedelta(hours=4, minutes=20)
            elif self.belt_size == BeltSizeChoice.LARGE:
                self.eta = now + timezone.timedelta(hours=10)
        # Mercocit belts have a different respawn time based on their size (https://wiki.eveuniversity.org/Asteroids_and_ore#Ore_Prospecting_Arrays)
        if self.belt_type == BeltTypeChoice.MERCOXIT_BELT:
            if self.belt_size == BeltSizeChoice.SMALL:
                self.eta = now + timezone.timedelta(minutes=5)
            elif self.belt_size == BeltSizeChoice.MEDIUM:
                self.eta = now + timezone.timedelta(minutes=10)
            elif self.belt_size == BeltSizeChoice.LARGE:
                self.eta = now + timezone.timedelta(hours=8)
            elif self.belt_size == BeltSizeChoice.ENORMOUS:
                self.eta = now + timezone.timedelta(hours=12)
        # Ice belts have a fixed respawn time of 8 hours (https://wiki.eveuniversity.org/Ice_harvesting#Ice_belts)
        if self.belt_type == BeltTypeChoice.ICE_BELT:
            if self.belt_size == BeltSizeChoice.ICE:
                self.eta = now + timezone.timedelta(hours=8)
        if self.eta is None:
            self.eta = None

    def save(self, *args, **kwargs):
        """
        Override the save method to automatically generate the ETA before saving the BeltTimer instance.
        This ensures that each timer has an accurate estimated time of respawn based on the belt type
        """
        self.generate_eta()

        # Generate a unique public_id if it is not already set
        if self.public_id == "":
            self.public_id = generate_unique_public_id()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.belt_id} - {self.belt_name} - {self.belt_type} - ETA: {self.eta}"

    @property
    def is_expired(self):
        """Check if the belt timer has expired based on the current time and the ETA."""
        if self.eta is None:
            return False
        return timezone.now() >= self.eta


class EveMarketPrice(models.Model):

    objects: EveMarketPriceManager = EveMarketPriceManager()

    class Meta:
        default_permissions = ()

    name = models.CharField(
        max_length=255,
    )
    eve_type = models.OneToOneField(
        ItemType,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="+",
    )
    average_price = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True
    )
    adjusted_price = models.DecimalField(max_digits=20, decimal_places=2)
    updated_at = models.DateTimeField()

    @property
    def get_compressed_price(self) -> float:
        """Calculate the compressed price based on the average price and the volume of the item."""
        if not self.average_price or not self.adjusted_price:
            return 0
        try:
            price = EveMarketPrice.objects.get(
                eve_type__name=f"Compressed {self.eve_type.name}"
            )
            return price.average_price
        except EveMarketPrice.DoesNotExist:
            return 0
