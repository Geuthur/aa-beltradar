"""Models for Belt Radar."""

# Standard Library
import uuid
from collections import defaultdict

# Django
from django.db import models
from django.utils import timezone
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

    def latest_entries(self, limit=2):
        return self.br_entries.order_by("-timestamp")[:limit]

    # pylint: disable=too-many-locals
    def mining_stats(self):
        """
        Unified mining statistics for this session.

        Returns a SurveyStatsSchema with aggregated data from all entries in this session.
        """
        # pylint: disable=import-outside-toplevel
        # AA Belt Radar
        from beltradar.api import schema

        entries = list(self.br_entries.select_related("eve_type").order_by("timestamp"))
        if len(entries) < 2:  # Not enough data points to calculate meaningful stats
            return schema.SurveyStatsSchema()

        snapshots: dict = defaultdict(float)
        snapshots_entries: dict[timezone.datetime, list[float]] = defaultdict(list)
        for entry in entries:
            try:
                vol = float(getattr(entry, "volume_left", None))
            except (TypeError, ValueError):
                vol = None
            if vol is None:
                continue
            ts = entry.timestamp.replace(microsecond=0)
            snapshots[ts] += vol
            snapshots_entries[ts].append(vol)

        # If we have no valid snapshots, return empty stats
        if not snapshots:
            return schema.SurveyStatsSchema()

        sorted_ts = sorted(snapshots.keys())
        start_ts, end_ts = sorted_ts[0], sorted_ts[-1]
        size, size_left = snapshots[start_ts], snapshots[end_ts]
        size_mined = max(0.0, size - size_left)
        duration = (end_ts - start_ts).total_seconds()

        vols_start = snapshots_entries.get(start_ts, [])
        vols_last = snapshots_entries.get(end_ts, [])
        asteroids_total = (
            len(vols_start) if vols_start else (len(vols_last) if vols_last else None)
        )
        asteroids_left = sum(1 for v in vols_last if v > 0.0) if vols_last else None

        rate = 0.0
        if len(sorted_ts) >= 2:
            prev_vol = snapshots[sorted_ts[-2]]
            mined_delta = max(0.0, prev_vol - size_left)
            time_delta = (end_ts - sorted_ts[-2]).total_seconds()
            if time_delta > 0 and mined_delta > 0:
                rate = mined_delta / time_delta
        elif duration > 0 and size_mined > 0:
            rate = size_mined / duration

        eta_seconds = size_left / rate if rate > 0 else None
        finish_dt = None
        if eta_seconds is not None:
            try:
                finish_dt = end_ts + timezone.timedelta(seconds=int(eta_seconds))
            except (OverflowError, OSError):
                pass
        progress_percent = (
            min(100.0, max(0.0, (size_mined / size) * 100.0)) if size else 0.0
        )

        return schema.SurveyStatsSchema(
            size=size,
            left=size_left,
            mined=size_mined,
            duration=duration,
            start=start_ts,
            end=end_ts,
            rate=rate,
            total_asteroids=asteroids_total,
            remaining_asteroids=asteroids_left,
            finish=finish_dt,
            progress_percent=progress_percent,
        )

    def last_entry(self):
        return self.br_entries.order_by("-timestamp").first()

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
