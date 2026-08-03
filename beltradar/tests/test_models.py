"""Test models for Belt Radar."""

# Standard Library
import hashlib
from datetime import datetime
from unittest.mock import patch

# Django
from django.utils import timezone

# Alliance Auth (External Libs)
from eve_sde.models.types import ItemType

# AA Belt Radar
from beltradar.models import BeltSurveyEntry, BeltSurveySession
from beltradar.models.helper.choices import BeltSizeChoice, BeltTypeChoice
from beltradar.tests import BeltRadarTestCase
from beltradar.tests.testdata.beltradar import BeltTimerFactory
from beltradar.tests.testdata.factory import ItemTypeFactory


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
            eve_type=ItemTypeFactory(),
            units=1000,
            volume_left=5000,
        )
        cls.entry2 = BeltSurveyEntry.objects.create(
            session=cls.session,
            snapshot=cls.unique_hash2,
            timestamp=cls.timestamp_2,
            eve_type=ItemTypeFactory(),
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
            eve_type=ItemTypeFactory(),
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

    @patch("beltradar.models.beltradar.timezone.now")
    def test_generate_eta(self, mock_now):
        """
        Test should generate eta for belt timer.
        """
        # given
        fixed_now = timezone.make_aware(datetime(2026, 1, 1, 12, 0, 0))
        mock_now.return_value = fixed_now
        belt_timer = BeltTimerFactory(
            belt_id=1,
            belt_name="Test Belt",
            belt_size=BeltSizeChoice.LARGE,
            belt_type=BeltTypeChoice.ASTEROID_BELT,
        )
        # when/then
        expected_eta = fixed_now + timezone.timedelta(hours=3)
        self.assertEqual(belt_timer.eta, expected_eta)

        # test arrey
        belt_timer2 = BeltTimerFactory(
            belt_id=2,
            belt_name="Test Belt 2",
            belt_size=BeltSizeChoice.MEDIUM,
            belt_type=BeltTypeChoice.ARREY_BELT,
        )
        # when/then
        expected_eta2 = fixed_now + timezone.timedelta(hours=4, minutes=20)
        self.assertEqual(belt_timer2.eta, expected_eta2)

        # test mercocit
        belt_timer3 = BeltTimerFactory(
            belt_id=3,
            belt_name="Test Belt 3",
            belt_size=BeltSizeChoice.SMALL,
            belt_type=BeltTypeChoice.MERCOXIT_BELT,
        )
        # when/then
        expected_eta3 = fixed_now + timezone.timedelta(minutes=5)
        self.assertEqual(belt_timer3.eta, expected_eta3)

        # test ice
        belt_timer4 = BeltTimerFactory(
            belt_id=4,
            belt_name="Test Belt 4",
            belt_size=BeltSizeChoice.ICE,
            belt_type=BeltTypeChoice.ICE_BELT,
        )
        # when/then
        expected_eta4 = fixed_now + timezone.timedelta(hours=8)
        self.assertEqual(belt_timer4.eta, expected_eta4)
