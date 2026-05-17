"""Models for Belt Radar."""

# Standard Library
import uuid

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
from beltradar.managers import BeltRadarManager, BeltSurveyEntryManager
from beltradar.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


class BeltSurveySession(models.Model):
    """Represents a single survey session for a belt, which can have multiple entries (BeltSurveyEntry)."""

    class Meta:
        default_permissions = ()  # Remove standard permissions

    objects: BeltRadarManager = BeltRadarManager()

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="br_user_sessions"
    )
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def first_entry(self):
        """Get the earliest survey entry in this session, or None if there are no entries."""
        return self.br_entries.order_by("timestamp").first()

    def first_entry_snapshot(self):
        """Get the snapshot identifier of the earliest entry in this session, or None if there are no entries."""
        first = self.first_entry()
        return first.snapshot if first else None

    def last_entry(self):
        """Get the most recent survey entry in this session, or None if there are no entries."""
        return self.br_entries.order_by("-timestamp").first()

    def last_entry_snapshot(self):
        """Get the snapshot identifier of the most recent entry in this session, or None if there are no entries."""
        last = self.last_entry()
        return last.snapshot if last else None

    @cached_property
    def belt_size_m3(self):
        """Calculate the total size of the belt in m3."""
        snapshot = self.first_entry_snapshot()
        qs = self.br_entries.filter(snapshot=snapshot)
        return sum(entry.units * entry.eve_type.volume for entry in qs)

    @cached_property
    def belt_left_m3(self):
        """Calculate the total volume left in the belt in m3."""
        snapshot = self.last_entry_snapshot()
        qs = self.br_entries.filter(snapshot=snapshot)
        return sum(entry.volume_left for entry in qs)

    @cached_property
    def remaining_asteroids(self):
        """Calculate the total number of remaining asteroids in the belt."""
        snapshot = self.last_entry_snapshot()
        qs = self.br_entries.filter(snapshot=snapshot)
        return sum(1 for entry in qs if entry.volume_left > 0)

    @cached_property
    def total_asteroids(self):
        """Calculate the total number of asteroids in the belt."""
        snapshot = self.first_entry_snapshot()
        qs = self.br_entries.filter(snapshot=snapshot)
        return sum(1 for entry in qs if entry.units > 0)

    @cached_property
    def progress_percent(self):
        """Calculate the percentage of the belt that has been mined."""
        size = float(self.belt_size_m3)
        if size == 0:
            return 0.0
        left = float(self.belt_left_m3)
        mined = size - left
        return (mined / size) * 100.0

    @cached_property
    def duration_seconds(self):
        """Calculate the duration of the survey session in seconds."""
        first = self.first_entry()
        last = self.last_entry()
        if not first or not last:
            return 0.0
        return (last.timestamp - first.timestamp).total_seconds()

    @cached_property
    def mining_rate_m3_per_s(self):
        """Calculate the average mining rate in m3/s."""
        duration = float(self.duration_seconds)
        if duration <= 0:
            return 0.0
        size = float(self.belt_size_m3)
        left = float(self.belt_left_m3)
        mined = size - left
        return mined / duration

    @cached_property
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
