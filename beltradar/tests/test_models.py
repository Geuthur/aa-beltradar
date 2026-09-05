"""Test models for Belt Radar."""

# Standard Library
import hashlib
from datetime import datetime
from unittest.mock import patch

# Django
from django.utils import timezone

# AA Belt Radar
from beltradar.models import BeltSurveySession, generate_unique_public_id
from beltradar.models.helper.choices import BeltSizeChoice, BeltTypeChoice
from beltradar.tests import BeltRadarTestCase
from beltradar.tests.testdata.beltradar import (
    BeltSessionFactory,
    BeltSurveyEntryFactory,
    BeltSurveySnapshotFactory,
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
        cls.unique_hash = generate_unique_public_id()
        cls.unique_hash2 = generate_unique_public_id()

    def test_get_entries_for_snapshot(self):
        """
        Test should return entries for given snapshot.
        """
        # Test Data
        snapshot = BeltSurveySnapshotFactory(session=self.session)
        BeltSurveyEntryFactory(snapshot=snapshot)
        # Test Action
        snapshots = self.session.br_snapshots.filter(identifier=snapshot.identifier)
        # Expected Result
        self.assertEqual(len(snapshots), 1)
        self.assertIn(snapshot, snapshots)

    def test_previous_entry_snapshot(self):
        """
        Test should return snapshot of previous entry for session.
        """
        # Test Data
        snapshot = BeltSurveySnapshotFactory(
            session=self.session, timestamp=self.timestamp, identifier=self.unique_hash
        )
        snapshot2 = BeltSurveySnapshotFactory(
            session=self.session,
            timestamp=self.timestamp_2,
            identifier=self.unique_hash2,
        )
        BeltSurveyEntryFactory(snapshot=snapshot)
        BeltSurveyEntryFactory(snapshot=snapshot2)

        # Test Action
        previous_snapshot = self.session.br_snapshots.previous_snapshot(snapshot2)
        # Expected Result
        self.assertEqual(previous_snapshot.identifier, self.unique_hash)

    def test_belt_size_m3(self):
        """
        Test should return total volume of ore in belt.
        """
        # Test Data
        snapshot = BeltSurveySnapshotFactory(session=self.session)
        BeltSurveyEntryFactory(
            snapshot=snapshot,
            volume_left=5000,
        )

        # Test Action
        belt_size_m3 = self.session.br_snapshots.first().belt_size_m3
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
                snapshot = BeltSurveySnapshotFactory(session=self.session)
                item_type = ItemTypeFactory(id=10_000 + index, name=ore_name)
                BeltSurveyEntryFactory(
                    snapshot=snapshot,
                    eve_type=item_type,
                    volume_left=volume_left,
                )

                self.assertEqual(
                    snapshot.session.br_snapshots.session_resolve_belt(),
                    (belt_type, belt_size),
                )
                snapshot.delete()

    def test_session_resolve_belt_with_mercoxit_grades(self):
        """Test that all Mercoxit grades resolve as a Mercoxit belt."""
        session = BeltSessionFactory()
        for index, ore_name in enumerate(
            ("Mercoxit", "Mercoxit II-Grade", "Mercoxit III-Grade")
        ):
            snapshot = BeltSurveySnapshotFactory(session=session)
            BeltSurveyEntryFactory(
                snapshot=snapshot,
                eve_type=ItemTypeFactory(id=20_000 + index, name=ore_name),
                volume_left=10000,
            )

        self.assertEqual(
            session.br_snapshots.session_resolve_belt(),
            (BeltTypeChoice.MERCOXIT_BELT, BeltSizeChoice.MEDIUM),
        )

    def test_session_resolve_belt_without_entries(self):
        """Test resolving a session without survey entries."""
        session = BeltSessionFactory()

        self.assertEqual(session.br_snapshots.session_resolve_belt(), (None, None))

    def test_is_timer_ready_should_return_false(self):
        """Test that a session with fewer than four snapshots is not ready for a timer."""
        session = BeltSessionFactory()
        blue_ice = ItemTypeFactory(id=30_000, name="Blue Ice")

        for _ in range(3):
            snapshot = BeltSurveySnapshotFactory(session=session)
            BeltSurveyEntryFactory(
                snapshot=snapshot,
                eve_type=blue_ice,
                volume_left=100_000,
            )

        self.assertFalse(session.is_timer_ready)

    def test_is_timer_ready_should_return_true(self):
        """Test that a session with four snapshots and a resolvable belt is ready for a timer."""
        session = BeltSessionFactory()
        blue_ice = ItemTypeFactory(id=30_000, name="Blue Ice")

        for _ in range(4):
            snapshot = BeltSurveySnapshotFactory(session=session)
            BeltSurveyEntryFactory(
                snapshot=snapshot,
                eve_type=blue_ice,
                volume_left=100_000,
            )

        self.assertTrue(session.is_timer_ready)

    def test_asteroids_count(self):
        """
        Test should return total units in belt.
        """
        # Test Data
        snapshot = BeltSurveySnapshotFactory(session=self.session)
        BeltSurveyEntryFactory(
            snapshot=snapshot,
        )

        # Test Action
        total_asteroids = self.session.br_snapshots.first().asteroid_count
        # Expected Result
        self.assertEqual(total_asteroids, 1)

    def test_progress_percent(self):
        """
        Test should return progress percent of belt survey.
        """
        # Test Data
        snapshot = BeltSurveySnapshotFactory(
            session=self.session, identifier=self.unique_hash, timestamp=self.timestamp
        )
        snapshot2 = BeltSurveySnapshotFactory(
            session=self.session,
            identifier=self.unique_hash2,
            timestamp=self.timestamp_2,
        )
        BeltSurveyEntryFactory(
            snapshot=snapshot,
            volume_left=5000,
        )
        BeltSurveyEntryFactory(
            snapshot=snapshot2,
            volume_left=2500,
        )
        # Test Action
        progress_percent = self.session.br_snapshots.session_progress_percentage(
            asteroids=snapshot.asteroids.all(),
            remaining_asteroids=snapshot2.asteroids.all(),
        )
        # Expected Result
        self.assertEqual(progress_percent, 50.0)

    def test_mining_rate_m3_per_s(self):
        """
        Test should return mining rate in m3/s.
        """
        # Test Data
        snapshot = BeltSurveySnapshotFactory(
            session=self.session, identifier=self.unique_hash, timestamp=self.timestamp
        )
        snapshot2 = BeltSurveySnapshotFactory(
            session=self.session,
            identifier=self.unique_hash2,
            timestamp=self.timestamp_2,
        )
        BeltSurveyEntryFactory(
            snapshot=snapshot,
            volume_left=5000,
        )
        BeltSurveyEntryFactory(
            snapshot=snapshot2,
            volume_left=2500,
        )
        # Test Action
        mining_rate = self.session.br_snapshots.rate_per_s()
        # Expected Result
        expected_rate = round(2500 / (3 * 3600), 2)
        self.assertEqual(mining_rate, expected_rate)

    def test_finish_eta(self):
        """
        Test should return finish eta for belt survey.
        """
        # Test Data
        snapshot = BeltSurveySnapshotFactory(
            session=self.session, timestamp=self.timestamp
        )
        snapshot2 = BeltSurveySnapshotFactory(
            session=self.session, timestamp=self.timestamp_2
        )

        BeltSurveyEntryFactory(
            snapshot=snapshot,
            volume_left=5000,
        )
        BeltSurveyEntryFactory(
            snapshot=snapshot2,
            volume_left=2500,
        )
        # Test Action
        finish_eta = self.session.br_snapshots.session_finish_eta(
            asteroids=snapshot.asteroids.all(),
            remaining_asteroids=snapshot2.asteroids.all(),
        )
        # Expected Result
        expected_eta = snapshot2.timestamp + timezone.timedelta(
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
        snapshot = BeltSurveySnapshotFactory(session=self.session)
        belt_survey = BeltSurveyEntryFactory(
            snapshot=snapshot,
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
        snapshot = BeltSurveySnapshotFactory(session=self.session)
        belt_survey = BeltSurveyEntryFactory(
            snapshot=snapshot,
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
        snapshot = BeltSurveySnapshotFactory(session=self.session)
        belt_survey = BeltSurveyEntryFactory(
            snapshot=snapshot,
            eve_type=item_type,
            price_compressed=2000.0,
            price=10000.0,
            volume_left=1000,
        )
        # when/then
        expected_income_per_h = (
            belt_survey.price / item_type.volume
        ) * self.session.br_snapshots.rate_per_s()
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
        snapshot = BeltSurveySnapshotFactory(session=self.session)
        belt_survey = BeltSurveyEntryFactory(
            snapshot=snapshot,
            eve_type=item_type,
            price_compressed=2000.0,
            price=10000.0,
            volume_left=500,
        )
        # when/then
        expected_income_cmp_per_h = (
            belt_survey.price_compressed / (item_type.volume / 100)
        ) * self.session.br_snapshots.rate_per_s()
        self.assertEqual(belt_survey.income_cmp_per_h, expected_income_cmp_per_h)

    def test_create_belt_timer(self):
        """
        Test should create a belt timer for the session.
        """
        # given
        item_type = ItemTypeFactory(
            name="Arkonor",
        )

        snapshot = BeltSurveySnapshotFactory(session=self.session)
        snapshot2 = BeltSurveySnapshotFactory(session=self.session)
        snapshot3 = BeltSurveySnapshotFactory(session=self.session)
        snapshot4 = BeltSurveySnapshotFactory(session=self.session)

        BeltSurveyEntryFactory(
            snapshot=snapshot,
            eve_type=item_type,
        )
        BeltSurveyEntryFactory(
            snapshot=snapshot2,
            eve_type=item_type,
        )
        BeltSurveyEntryFactory(
            snapshot=snapshot3,
            eve_type=item_type,
        )
        BeltSurveyEntryFactory(
            snapshot=snapshot4,
            eve_type=item_type,
        )
        # when
        belt_timer = self.session.create_belt_timer()
        # then
        self.assertIsNotNone(belt_timer)
        self.assertEqual(belt_timer.belt_name, self.session.name)
