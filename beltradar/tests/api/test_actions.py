# Standard Library
from datetime import datetime, timedelta

# Django
from django.urls import reverse
from django.utils import timezone

# AA Belt Radar
from beltradar.api.helpers.actions import (
    belt_timer_manage_actions,
    get_snapshot_delete_action,
    session_belt_timer_actions,
    session_manage_actions,
)
from beltradar.models import generate_unique_public_id
from beltradar.tests import BeltRadarTestCase
from beltradar.tests.testdata.beltradar import (
    BeltSessionFactory,
    BeltSnapshotFactory,
    BeltSurveyEntryFactory,
    BeltTimerFactory,
    UserMainFactory,
)

MODULE_PATH = "beltradar.api.helpers."
API_URL = "beltradar:api"


class TestActionHelper(BeltRadarTestCase):
    """Test Action Helper."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.timestamp = timezone.make_aware(datetime(2024, 1, 1, 12, 0, 0))

    def test_session_manage_actions_should_all(self):
        """Test session manage actions should show all actions."""
        # Test Data
        session = BeltSessionFactory(owner=self.user)

        # Test Action
        request = self.factory.get(reverse("beltradar:react_base"))
        request.user = self.user
        response = session_manage_actions(request=request, session=session)

        # Expected Result
        self.assertEqual(response.update.modal_id, "beltradar-accept-modify-session")
        self.assertEqual(response.delete.modal_id, "beltradar-accept-delete-session")

    def _create_snapshots(self, session, volumes):
        """Create one snapshot per volume, one hour apart."""
        for hours, volume_left in enumerate(volumes):
            snapshot = BeltSnapshotFactory(
                session=session,
                timestamp=self.timestamp + timedelta(hours=hours),
                identifier=generate_unique_public_id(),
            )
            BeltSurveyEntryFactory(snapshot=snapshot, volume_left=volume_left)

    def test_session_belt_timer_actions_should_show_create_button(self):
        """Test session belt timer actions should show the create action when 10% is left."""
        # Test Data
        session = BeltSessionFactory(owner=self.user)
        self._create_snapshots(session, [1_000_000, 500_000, 100_000])

        # Test Action
        request = self.factory.get(reverse("beltradar:react_base"))
        request.user = self.user
        response = session_belt_timer_actions(
            request=request, public_id=session.public_id
        )

        # Expected Result
        self.assertIsNotNone(response.create)
        self.assertEqual(response.create.modal_id, "beltradar-accept-create-belt-timer")

    def test_session_belt_timer_actions_should_show_delete_button(self):
        """Test session belt timer actions should show the update and delete actions."""
        # Test Data
        session = BeltSessionFactory(owner=self.user)
        self._create_snapshots(session, [1_000_000, 500_000, 100_000])

        BeltTimerFactory(
            owner=self.user,
            public_id=session.public_id,
            session=session,
        )

        # Test Action
        request = self.factory.get(reverse("beltradar:react_base"))
        request.user = self.user
        response = session_belt_timer_actions(
            request=request, public_id=session.public_id
        )

        # Expected Result
        self.assertEqual(response.update.modal_id, "beltradar-accept-modify-belt-timer")
        self.assertEqual(response.delete.modal_id, "beltradar-accept-delete-belt-timer")

    def test_session_belt_timer_actions_should_empty_string_when_more_than_10_percent_left(
        self,
    ):
        """Test session belt timer actions should return None while more than 10% is left."""
        # Test Data
        session = BeltSessionFactory(owner=self.user)
        self._create_snapshots(session, [1_000_000, 500_000, 100_001])

        # Test Action
        request = self.factory.get(reverse("beltradar:react_base"))
        request.user = self.user
        response = session_belt_timer_actions(
            request=request, public_id=session.public_id
        )

        # Expected Result
        self.assertIsNone(response)

    def test_session_belt_timer_actions_should_empty_string(self):
        """Test session belt timer actions should return None for sessions without snapshots."""
        # Test Data
        session = BeltSessionFactory(owner=self.user)

        # Test Action
        request = self.factory.get(reverse("beltradar:react_base"))
        request.user = self.user
        response = session_belt_timer_actions(
            request=request, public_id=session.public_id
        )

        # Expected Result
        self.assertIsNone(response)

    def test_belt_timer_manage_actions_should_show_all(self):
        """Test belt timer manage actions should show all actions."""
        # Test Data
        timer = BeltTimerFactory(
            owner=self.user,
        )

        # Test Action
        request = self.factory.get(reverse("beltradar:react_base"))
        request.user = self.user
        response = belt_timer_manage_actions(request=request, timer=timer)

        # Expected Result
        self.assertEqual(response.update.modal_id, "beltradar-accept-modify-belt-timer")
        self.assertEqual(response.delete.modal_id, "beltradar-accept-delete-belt-timer")

    def test_belt_timer_manage_actions_should_show_modify_when_session_linked(
        self,
    ):
        """Test belt timer manage actions should show modify even if linked to a session."""
        # Test Data
        session = BeltSessionFactory(owner=self.user)
        timer = BeltTimerFactory(
            owner=self.user,
            session=session,
        )

        # Test Action
        request = self.factory.get(reverse("beltradar:react_base"))
        request.user = self.user
        response = belt_timer_manage_actions(request=request, timer=timer)

        # Expected Result
        self.assertEqual(response.update.modal_id, "beltradar-accept-modify-belt-timer")
        self.assertEqual(response.delete.modal_id, "beltradar-accept-delete-belt-timer")

    def test_belt_timer_manage_actions_should_empty_string(self):
        """Test belt timer manage actions should return None for unauthorized users."""
        # Test Data
        timer = BeltTimerFactory(
            owner=self.user,
        )

        # Test Action
        request = self.factory.get(reverse("beltradar:react_base"))
        request.user = UserMainFactory()
        response = belt_timer_manage_actions(request=request, timer=timer)

        # Expected Result
        self.assertIsNone(response)

    def test_get_snapshot_delete_action_should_show_delete_action(self):
        """Test get snapshot delete action should return the delete action."""
        # Test Data
        session = BeltSessionFactory(owner=self.user)
        snapshot = BeltSnapshotFactory(session=session)

        # Test Action
        request = self.factory.get(reverse("beltradar:react_base"))
        request.user = self.user
        response = get_snapshot_delete_action(
            request=request, public_id=session.public_id, identifier=snapshot.identifier
        )

        # Expected Result
        self.assertEqual(response.modal_id, "beltradar-accept-delete-snapshot")

    def test_get_snapshot_delete_action_should_empty_string(self):
        """Test get snapshot delete action should return None for unauthorized users."""
        # Test Data
        session = BeltSessionFactory(owner=self.user)
        snapshot = BeltSnapshotFactory(session=session)

        # Test Action
        request = self.factory.get(reverse("beltradar:react_base"))
        request.user = UserMainFactory()
        response = get_snapshot_delete_action(
            request=request, public_id=session.public_id, identifier=snapshot.identifier
        )

        # Expected Result
        self.assertIsNone(response)
