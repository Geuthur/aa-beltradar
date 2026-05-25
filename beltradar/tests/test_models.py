"""Test models for Belt Radar."""

# Standard Library
import hashlib
from datetime import datetime

# Django
from django.utils import timezone

# Alliance Auth (External Libs)
from eve_sde.models.types import ItemType

# AA Belt Radar
from beltradar.models import BeltSurveyEntry, BeltSurveySession
from beltradar.tests import BeltRadarTestCase


class TestBeltSurveySessionModel(BeltRadarTestCase):
    """Test BeltSurveySession model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.session = BeltSurveySession.objects.create(
            name="Test Session", owner=cls.user
        )
        cls.timestamp = timezone.make_aware(datetime(2024, 1, 1, 12, 0, 0))
        cls.timestamp_2 = timezone.make_aware(datetime(2024, 1, 1, 15, 0, 0))
        cls.unique_hash = hashlib.sha256(b"Test Data").hexdigest()
        cls.unique_hash2 = hashlib.sha256(b"Test Data 2").hexdigest()
        cls.entry1 = BeltSurveyEntry.objects.create(
            session=cls.session,
            snapshot=cls.unique_hash,
            timestamp=cls.timestamp,
            eve_type=ItemType.objects.get(id=1),
            units=1000,
            volume_left=5000,
        )
        cls.entry2 = BeltSurveyEntry.objects.create(
            session=cls.session,
            snapshot=cls.unique_hash2,
            timestamp=cls.timestamp_2,
            eve_type=ItemType.objects.get(id=1),
            units=500,
            volume_left=2500,
        )

    def test_get_entries_for_snapshot(self):
        """
        Test should return entries for given snapshot.
        """
        # when
        entries = self.session.get_entries_for_snapshot(snapshot=self.unique_hash)
        # then
        self.assertEqual(len(entries), 1)
        self.assertIn(self.entry1, entries)

    def test_get_first_entry(self):
        """
        Test should return first entry for session.
        """
        # when
        first_entry = self.session.first_entry()
        # then
        self.assertEqual(first_entry, self.entry1)

    def test_get_first_entry_snapshot(self):
        """
        Test should return snapshot of first entry for session.
        """
        # when
        first_entry_snapshot = self.session.first_entry_snapshot
        # then
        self.assertEqual(first_entry_snapshot, self.unique_hash)

    def test_last_entry(self):
        """
        Test should return last entry for session.
        """
        # when
        last_entry = self.session.last_entry()
        # then
        self.assertEqual(last_entry, self.entry2)

    def test_last_entry_snapshot(self):
        """
        Test should return snapshot of last entry for session.
        """
        # when
        last_entry_snapshot = self.session.last_entry_snapshot
        # then
        self.assertEqual(last_entry_snapshot, self.unique_hash2)

    def test_last_entry_timestamp(self):
        """
        Test should return timestamp of last entry for session.
        """
        # when
        last_entry_timestamp = self.session.last_entry_timestamp
        # then
        self.assertEqual(last_entry_timestamp, self.entry2.timestamp)

    def test_previous_entry_snapshot(self):
        """
        Test should return snapshot of previous entry for session.
        """
        # when
        previous_entry_snapshot = self.session.previous_entry_snapshot
        # then
        self.assertEqual(previous_entry_snapshot, self.unique_hash)

    def test_belt_size_m3(self):
        """
        Test should return total volume of ore in belt.
        """
        # when
        belt_size_m3 = self.session.belt_size_m3
        # then
        self.assertEqual(belt_size_m3, 5000)

    def test_belt_left_m3(self):
        """
        Test should return total volume left in belt.
        """
        # when
        belt_left_m3 = self.session.belt_left_m3
        # then
        self.assertEqual(belt_left_m3, 2500)

    def test_remaining_asteroids(self):
        """
        Test should return total units left in belt.
        """
        # when
        remaining_asteroids = self.session.remaining_asteroids
        # then
        self.assertEqual(remaining_asteroids, 1)

    def test_total_asteroids(self):
        """
        Test should return total units in belt.
        """
        # given
        BeltSurveyEntry.objects.create(
            session=self.session,
            snapshot=self.unique_hash,
            timestamp=self.timestamp,
            eve_type=ItemType.objects.get(id=2),
            units=500,
            volume_left=2500,
        )
        # when
        total_asteroids = self.session.total_asteroids
        # then
        self.assertEqual(total_asteroids, 2)

    def test_progress_percent(self):
        """
        Test should return progress percent of belt survey.
        """
        # when
        progress_percent = self.session.progress_percent
        # then
        self.assertEqual(progress_percent, 50.0)

    def test_previos_entry_duration(self):
        """
        Test should return duration between last and previous entry.
        """
        # when
        previous_entry_duration = self.session.previous_entry_duration
        # then
        self.assertEqual(previous_entry_duration, 3 * 3600)

    def test_mining_rate_m3_per_s(self):
        """
        Test should return mining rate in m3/s.
        """
        # when
        mining_rate = self.session.mining_rate_m3_per_s
        # then
        self.assertEqual(mining_rate, 2500 / (3 * 3600))

    def test_finish_eta(self):
        """
        Test should return finish eta for belt survey.
        """
        # when
        finish_eta = self.session.finish_eta
        # then
        expected_eta = self.entry2.timestamp + timezone.timedelta(
            seconds=2500 / (2500 / (3 * 3600))
        )
        self.assertEqual(finish_eta, expected_eta)

    def test_is_fresh_false(self):
        """
        Test should return False if session is not fresh.
        """
        # when
        is_fresh = self.session.is_fresh
        # then
        self.assertFalse(is_fresh)
