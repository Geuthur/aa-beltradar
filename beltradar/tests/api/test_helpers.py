# Third Party
from evesde_factory.eve_sde import ItemTypeFactory

# Django
from django.urls import reverse

# AA Belt Radar
from beltradar.api.helpers.icons import (
    belt_timer_manage_action_icons,
    get_session_delete_button,
    get_snapshot_delete_button,
    session_belt_timer_action_icons,
    session_manage_action_icons,
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


class TestIconHelper(BeltRadarTestCase):
    """Test Icon Helper."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_session_manage_action_icons_should_all(self):
        """Test session manage action icons should show all action icons."""
        # Test Data
        session = BeltSessionFactory(owner=self.user)

        # Test Action
        request = self.factory.get(reverse("beltradar:react_base"))
        request.user = self.user
        response = session_manage_action_icons(request=request, session=session)

        # Expected Result
        self.assertEqual(response.update.icon, "fa-solid fa-wrench")
        self.assertEqual(response.delete.icon, "fa-solid fa-trash")

    def test_session_belt_timer_action_icons_should_show_create_button(self):
        """Test session belt timer action icons should show the create button icon."""
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
        response = session_belt_timer_action_icons(
            request=request, public_id=snapshot.session.public_id
        )

        # Expected Result
        self.assertIsNotNone(response.create)
        self.assertEqual(response.create.title, "Create Belt Timer")

    def test_session_belt_timer_action_icons_should_show_delete_button(self):
        """Test session belt timer action icons should show the delete button."""
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
        response = session_belt_timer_action_icons(
            request=request, public_id=snapshot.session.public_id
        )

        # Expected Result
        self.assertEqual(response.update.title, "Modify Belt Timer")
        self.assertEqual(response.delete.title, "Delete Belt Timer")

    def test_session_belt_timer_action_icons_should_empty_string(self):
        """Test session belt timer action icons should return None for unauthorized users."""
        # Test Data
        session = BeltSessionFactory(owner=self.user)

        # Test Action
        request = self.factory.get(reverse("beltradar:react_base"))
        request.user = self.user
        response = session_belt_timer_action_icons(
            request=request, public_id=session.public_id
        )

        # Expected Result
        self.assertIsNone(response)

    def test_belt_timer_manage_action_icons_should_show_all(self):
        """Test belt timer manage action icons should show all action icons."""
        # Test Data
        timer = BeltTimerFactory(
            owner=self.user,
        )

        # Test Action
        request = self.factory.get(reverse("beltradar:react_base"))
        request.user = self.user
        response = belt_timer_manage_action_icons(request=request, timer=timer)

        # Expected Result
        self.assertEqual(response.update.title, "Modify Belt Timer")
        self.assertEqual(response.delete.title, "Delete Belt Timer")

    def test_belt_timer_manage_action_icons_should_show_modify_when_session_linked(
        self,
    ):
        """Test belt timer manage action icons should show modify icon even if linked to a session."""
        # Test Data
        session = BeltSessionFactory(owner=self.user)
        timer = BeltTimerFactory(
            owner=self.user,
            session=session,
        )

        # Test Action
        request = self.factory.get(reverse("beltradar:react_base"))
        request.user = self.user
        response = belt_timer_manage_action_icons(request=request, timer=timer)

        # Expected Result
        self.assertEqual(response.update.title, "Modify Belt Timer")
        self.assertEqual(response.delete.title, "Delete Belt Timer")

    def test_belt_timer_manage_action_icons_should_empty_string(self):
        """Test belt timer manage action icons should return None for unauthorized users."""
        # Test Data
        timer = BeltTimerFactory(
            owner=self.user,
        )

        # Test Action
        request = self.factory.get(reverse("beltradar:react_base"))
        request.user = UserMainFactory()
        response = belt_timer_manage_action_icons(request=request, timer=timer)

        # Expected Result
        self.assertIsNone(response)

    def test_get_snapshot_delete_button_should_show_delete_button(self):
        """Test get snapshot delete button should return the delete button HTML."""
        # Test Data
        session = BeltSessionFactory(owner=self.user)
        snapshot = BeltSnapshotFactory(session=session)

        # Test Action
        request = self.factory.get(reverse("beltradar:react_base"))
        request.user = self.user
        response = get_snapshot_delete_button(
            request=request, public_id=session.public_id, identifier=snapshot.identifier
        )

        # Expected Result
        self.assertEqual(response.title, "Delete Snapshot")

    def test_get_snapshot_delete_button_should_empty_string(self):
        """Test get snapshot delete button should return None for unauthorized users."""
        # Test Data
        session = BeltSessionFactory(owner=self.user)
        snapshot = BeltSnapshotFactory(session=session)

        # Test Action
        request = self.factory.get(reverse("beltradar:react_base"))
        request.user = UserMainFactory()
        response = get_snapshot_delete_button(
            request=request, public_id=session.public_id, identifier=snapshot.identifier
        )

        # Expected Result
        self.assertIsNone(response)

    def test_get_session_delete_button_should_show_delete_button(self):
        """Test get session delete button should return the delete button HTML."""
        # Test Data
        session = BeltSessionFactory(owner=self.user)

        # Test Action
        request = self.factory.get(reverse("beltradar:react_base"))
        request.user = self.user
        response = get_session_delete_button(
            request=request, public_id=session.public_id
        )

        # Expected Result
        self.assertEqual(response.title, "Delete Session")

    def test_get_session_delete_button_should_empty_string(self):
        """Test get session delete button should return None for unauthorized users."""
        # Test Data
        session = BeltSessionFactory(owner=self.user)

        # Test Action
        request = self.factory.get(reverse("beltradar:react_base"))
        request.user = UserMainFactory()
        response = get_session_delete_button(
            request=request, public_id=session.public_id
        )

        # Expected Result
        self.assertEqual(response, "")
