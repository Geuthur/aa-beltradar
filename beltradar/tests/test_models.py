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
from beltradar.tests.testdata.beltradar import (
    BeltSessionFactory,
    BeltSurveyEntryFactory,
    BeltTimerFactory,
)
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

    def test_get_entries_for_snapshot(self):
        """
        Test should return entries for given snapshot.
        """
        # Test Data
        entry = BeltSurveyEntryFactory(
            session=self.session,
            snapshot=self.unique_hash,
        )
        # Test Action
        entries = self.session.br_entries.for_snapshot(snapshot=self.unique_hash)
        # Expected Result
        self.assertEqual(len(entries), 1)
        self.assertIn(entry, entries)

    def test_previous_entry_snapshot(self):
        """
        Test should return snapshot of previous entry for session.
        """
        # Test Data
        BeltSurveyEntryFactory(
            session=self.session,
            snapshot=self.unique_hash,
            timestamp=self.timestamp,
        )
        last_entry = BeltSurveyEntryFactory(
            session=self.session,
            snapshot=self.unique_hash2,
            timestamp=self.timestamp_2,
        )

        # Test Action
        previous_entry_snapshot = self.session.br_entries.previous_snapshot(
            last_entry.snapshot
        )
        # Expected Result
        self.assertEqual(previous_entry_snapshot, self.unique_hash)

    def test_belt_size_m3(self):
        """
        Test should return total volume of ore in belt.
        """
        # Test Data
        BeltSurveyEntryFactory(
            session=self.session,
            snapshot=self.unique_hash,
            timestamp=self.timestamp,
            volume_left=5000,
        )

        # Test Action
        belt_size_m3 = self.session.br_entries.belt_size_m3()
        # Expected Result
        self.assertEqual(belt_size_m3, 5000)

    def test_session_resolve_belt(self):
        """Test resolving the type and size from the newest snapshot."""
        test_cases = (
            ("Arkonor", 1_880_000, BeltTypeChoice.ASTEROID_BELT, BeltSizeChoice.LARGE),
            ("Mercoxit", 40_000, BeltTypeChoice.MERCOXIT_BELT, BeltSizeChoice.MEDIUM),
            ("Blue Ice", 100_000, BeltTypeChoice.ICE_BELT, BeltSizeChoice.ICE),
            ("Griemeer", 3_000_000, BeltTypeChoice.ARRAY_BELT, BeltSizeChoice.MEDIUM),
        )

        for index, (ore_name, volume_left, belt_type, belt_size) in enumerate(
            test_cases
        ):
            with self.subTest(ore_name=ore_name):
                session = BeltSessionFactory()
                item_type = ItemTypeFactory(id=10_000 + index, name=ore_name)
                BeltSurveyEntryFactory(
                    session=session,
                    snapshot=f"snapshot-{index}",
                    eve_type=item_type,
                    volume_left=volume_left,
                )

                self.assertEqual(
                    session.br_entries.session_resolve_belt(),
                    (belt_type, belt_size),
                )

    def test_session_resolve_belt_with_mercoxit_grades(self):
        """Test that all Mercoxit grades resolve as a Mercoxit belt."""
        session = BeltSessionFactory()
        for index, ore_name in enumerate(
            ("Mercoxit", "Mercoxit II-Grade", "Mercoxit III-Grade")
        ):
            BeltSurveyEntryFactory(
                session=session,
                snapshot="mercoxit-grades",
                eve_type=ItemTypeFactory(id=20_000 + index, name=ore_name),
                volume_left=40_000 / 3,
            )

        self.assertEqual(
            session.br_entries.session_resolve_belt(),
            (BeltTypeChoice.MERCOXIT_BELT, BeltSizeChoice.MEDIUM),
        )

    def test_session_resolve_belt_without_entries(self):
        """Test resolving a session without survey entries."""
        session = BeltSessionFactory()

        self.assertEqual(session.br_entries.session_resolve_belt(), (None, None))

    def test_is_timer_ready_requires_four_resolved_snapshots(self):
        """Test timer readiness requires four snapshots and a resolvable belt."""
        session = BeltSessionFactory()
        blue_ice = ItemTypeFactory(id=30_000, name="Blue Ice")

        for index in range(3):
            BeltSurveyEntryFactory(
                session=session,
                snapshot=f"snapshot-{index}",
                eve_type=blue_ice,
                volume_left=100_000,
            )

        self.assertFalse(session.is_timer_ready)

        BeltSurveyEntryFactory(
            session=session,
            snapshot="snapshot-3",
            eve_type=blue_ice,
            volume_left=100_000,
        )

        self.assertTrue(session.is_timer_ready)

    def test_asteroids_count(self):
        """
        Test should return total units in belt.
        """
        # Test Data
        BeltSurveyEntryFactory(
            session=self.session,
            snapshot=self.unique_hash,
            timestamp=self.timestamp,
        )

        # Test Action
        total_asteroids = self.session.br_entries.asteroid_count()
        # Expected Result
        self.assertEqual(total_asteroids, 1)

    def test_progress_percent(self):
        """
        Test should return progress percent of belt survey.
        """
        # Test Data
        BeltSurveyEntryFactory(
            session=self.session,
            snapshot=self.unique_hash,
            timestamp=self.timestamp,
            volume_left=5000,
        )
        BeltSurveyEntryFactory(
            session=self.session,
            snapshot=self.unique_hash2,
            timestamp=self.timestamp_2,
            volume_left=2500,
        )
        # Test Action
        progress_percent = self.session.br_entries.session_progress_percentage()
        # Expected Result
        self.assertEqual(progress_percent, 50.0)

    def test_previos_entry_duration(self):
        """
        Test should return duration between last and previous entry.
        """
        # Test Data
        first = BeltSurveyEntryFactory(
            session=self.session,
            snapshot=self.unique_hash,
            timestamp=self.timestamp,
        )
        last = BeltSurveyEntryFactory(
            session=self.session,
            snapshot=self.unique_hash2,
            timestamp=self.timestamp_2,
        )
        # Test Action
        previous_entry_duration = self.session.br_entries.duration(
            first_entry=first, last_entry=last
        )
        # Expected Result
        self.assertEqual(previous_entry_duration, 3 * 3600)

    def test_mining_rate_m3_per_s(self):
        """
        Test should return mining rate in m3/s.
        """
        # Test Data
        BeltSurveyEntryFactory(
            session=self.session,
            snapshot=self.unique_hash,
            timestamp=self.timestamp,
            volume_left=5000,
        )
        BeltSurveyEntryFactory(
            session=self.session,
            snapshot=self.unique_hash2,
            timestamp=self.timestamp_2,
            volume_left=2500,
        )
        # Test Action
        mining_rate = self.session.br_entries.rate_per_s()
        # Expected Result
        expected_rate = round(2500 / (3 * 3600), 2)
        self.assertEqual(mining_rate, expected_rate)

    def test_finish_eta(self):
        """
        Test should return finish eta for belt survey.
        """
        # Test Data
        BeltSurveyEntryFactory(
            session=self.session,
            snapshot=self.unique_hash,
            timestamp=self.timestamp,
            volume_left=5000,
        )
        entry2 = BeltSurveyEntryFactory(
            session=self.session,
            snapshot=self.unique_hash2,
            timestamp=self.timestamp_2,
            volume_left=2500,
        )
        # Test Action
        finish_eta = self.session.br_entries.session_finish_eta()
        # Expected Result
        expected_eta = entry2.timestamp + timezone.timedelta(
            seconds=2500 / (2500 / (3 * 3600))
        )
        self.assertEqual(finish_eta, expected_eta)

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
            belt_type=BeltTypeChoice.ARRAY_BELT,
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

    def test_price_per_m3(self):
        """
        Test should return price per m3 for belt timer.
        """
        # given
        item_type = ItemTypeFactory(
            id=1,
            name="Test Ore",
            volume=10.0,
        )
        belt_survey = BeltSurveyEntryFactory(
            session=self.session,
            eve_type=item_type,
            price_compressed=1000.0,
            price=5000.0,
        )
        # when/then
        expected_price_per_m3 = belt_survey.price / item_type.volume
        self.assertEqual(belt_survey.price_per_m3, expected_price_per_m3)

    def test_price_cmp_per_m3(self):
        """
        Test should return price per m3 for belt timer with cmp ore type.
        """
        # given
        item_type = ItemTypeFactory(
            id=2,
            name="Test CMP Ore",
            volume=5.0,
        )
        belt_survey = BeltSurveyEntryFactory(
            session=self.session,
            eve_type=item_type,
            price_compressed=1000.0,
            price=5000.0,
        )
        # when/then
        expected_price_per_m3 = belt_survey.price_compressed / (item_type.volume / 100)
        self.assertEqual(belt_survey.price_cmp_per_m3, expected_price_per_m3)

    def test_income_per_h(self):
        """
        Test should return income per hour for belt timer.
        """
        # given
        item_type = ItemTypeFactory(
            id=3,
            name="Test Ore 3",
            volume=20.0,
        )
        belt_survey = BeltSurveyEntryFactory(
            session=self.session,
            eve_type=item_type,
            price_compressed=2000.0,
            price=10000.0,
            volume_left=1000,
        )
        # when/then
        expected_income_per_h = (
            belt_survey.price / item_type.volume
        ) * self.session.br_entries.rate_per_s()
        self.assertEqual(belt_survey.income_per_h, expected_income_per_h)

    def test_income_cmp_per_h(self):
        """
        Test should return income per hour for belt timer with cmp ore type.
        """
        # given
        item_type = ItemTypeFactory(
            id=4,
            name="Test CMP Ore 4",
            volume=10.0,
        )
        belt_survey = BeltSurveyEntryFactory(
            session=self.session,
            eve_type=item_type,
            price_compressed=2000.0,
            price=10000.0,
            volume_left=500,
        )
        # when/then
        expected_income_cmp_per_h = (
            belt_survey.price_compressed / (item_type.volume / 100)
        ) * self.session.br_entries.rate_per_s()
        self.assertEqual(belt_survey.income_cmp_per_h, expected_income_cmp_per_h)

    def test_create_belt_timer(self):
        """
        Test should create a belt timer for the session.
        """
        # given
        item_type = ItemTypeFactory(
            name="Arkonor",
        )
        BeltSurveyEntryFactory(
            session=self.session,
            eve_type=item_type,
        )
        BeltSurveyEntryFactory(
            session=self.session,
            eve_type=item_type,
        )
        BeltSurveyEntryFactory(
            session=self.session,
            eve_type=item_type,
        )
        BeltSurveyEntryFactory(
            session=self.session,
            eve_type=item_type,
        )
        # when
        belt_timer = self.session.create_belt_timer()
        # then
        self.assertIsNotNone(belt_timer)
        self.assertEqual(belt_timer.belt_name, self.session.name)
