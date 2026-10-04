# Third Party
from evesde_factory.eve_sde import ItemTypeFactory

# Django
from django.urls import reverse

# AA Belt Radar
from beltradar.api.helpers.actions import (
    belt_timer_manage_actions,
    get_snapshot_delete_action,
    session_belt_timer_actions,
    session_manage_actions,
)
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

    def test_session_belt_timer_actions_should_show_create_button(self):
        """Test session belt timer actions should show the create action."""
        # Test Data
        item_type = ItemTypeFactory(
            name="Arkonor",
        )
        session = BeltSessionFactory(owner=self.user)
        snapshot = BeltSnapshotFactory(session=session)
        snapshot2 = BeltSnapshotFactory(session=session)
        snapshot3 = BeltSnapshotFactory(session=session)
        snapshot4 = BeltSnapshotFactory(session=session)

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

        # Test Action
        request = self.factory.get(reverse("beltradar:react_base"))
        request.user = self.user
        response = session_belt_timer_actions(
            request=request, public_id=snapshot.session.public_id
        )

        # Expected Result
        self.assertIsNotNone(response.create)
        self.assertEqual(response.create.modal_id, "beltradar-accept-create-belt-timer")

    def test_session_belt_timer_actions_should_show_delete_button(self):
        """Test session belt timer actions should show the update and delete actions."""
        # Test Data
        item_type = ItemTypeFactory(
            name="Arkonor",
        )
        session = BeltSessionFactory(owner=self.user)
        snapshot = BeltSnapshotFactory(session=session)
        snapshot2 = BeltSnapshotFactory(session=session)
        snapshot3 = BeltSnapshotFactory(session=session)
        snapshot4 = BeltSnapshotFactory(session=session)

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

        BeltTimerFactory(
            owner=self.user,
            public_id=session.public_id,
            session=session,
        )

        # Test Action
        request = self.factory.get(reverse("beltradar:react_base"))
        request.user = self.user
        response = session_belt_timer_actions(
            request=request, public_id=snapshot.session.public_id
        )

        # Expected Result
        self.assertEqual(response.update.modal_id, "beltradar-accept-modify-belt-timer")
        self.assertEqual(response.delete.modal_id, "beltradar-accept-delete-belt-timer")

    def test_session_belt_timer_actions_should_empty_string(self):
        """Test session belt timer actions should return None for sessions that are not ready."""
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
