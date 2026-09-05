# Standard Library
import json
from http import HTTPStatus

# Django
from django.urls import reverse

# AA Belt Radar
from beltradar.models import BeltTimer
from beltradar.tests import BeltRadarTestCase
from beltradar.tests.testdata.beltradar import (
    BeltSessionFactory,
    BeltSnapshotFactory,
    BeltSurveyEntryFactory,
    BeltTimerFactory,
    ItemTypeFactory,
    UserMainFactory,
)

MODULE_PATH = "beltradar.api.helpers."
API_URL = "beltradar:api"


class TestApiEndpoints(BeltRadarTestCase):
    """Test API Endpoints."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_get_session_stats_should_200(self):
        """
        Test should return 200 OK when user has permissions and resource exists.
        """
        # Test Data
        session = BeltSessionFactory(owner=self.user)
        url = reverse(
            f"{API_URL}:get_session_stats", kwargs={"public_id": session.public_id}
        )
        self.client.force_login(self.user)

        # Test Action
        response = self.client.get(url)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_session_stats_should_403(self):
        """
        Test should return 403 Forbidden when user lacks permissions.
        """
        # Test Data
        session = BeltSessionFactory(owner=self.user)
        user_no_permission = UserMainFactory(permissions__=[])
        url = reverse(
            f"{API_URL}:get_session_stats", kwargs={"public_id": session.public_id}
        )
        self.client.force_login(user_no_permission)

        # Test Action
        response = self.client.get(url)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_get_session_stats_should_404(self):
        """
        Test should return 404 Not Found when the session does not exist.
        """
        # Test Data
        url = reverse(
            f"{API_URL}:get_session_stats",
            kwargs={"public_id": "non_existent_public_id"},
        )
        self.client.force_login(self.user)

        # Test Action
        response = self.client.get(url)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_get_my_sessions_should_200(self):
        """
        Test should return 200 OK when user has permissions and resource exists.
        """
        # Test Data
        BeltSessionFactory(owner=self.user)
        url = reverse(
            f"{API_URL}:get_my_sessions",
            kwargs={"character_id": self.user.profile.main_character.character_id},
        )
        self.client.force_login(self.user)

        # Test Action
        response = self.client.get(url)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_my_sessions_should_403(self):
        """
        Test should return 403 Forbidden when user lacks permissions.
        """
        # Test Data
        BeltSessionFactory(owner=self.user)
        user_no_permission = UserMainFactory(permissions__=[])
        url = reverse(
            f"{API_URL}:get_my_sessions",
            kwargs={"character_id": self.user.profile.main_character.character_id},
        )
        self.client.force_login(user_no_permission)

        # Test Action
        response = self.client.get(url)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_get_public_sessions_should_200(self):
        """
        Test should return 200 OK when user has permissions and resource exists.
        """
        # Test Data
        BeltSessionFactory(owner=self.user)
        BeltSessionFactory(owner=self.user)
        url = reverse(f"{API_URL}:get_public_sessions")
        self.client.force_login(self.user)

        # Test Action
        response = self.client.get(url)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_my_belt_timer_should_200(self):
        """
        Test should return 200 OK when user has permissions and resource exists.
        """
        # Test Data
        BeltTimerFactory(owner=self.user)
        url = reverse(
            f"{API_URL}:get_my_belt_timer",
            kwargs={"character_id": self.user.profile.main_character.character_id},
        )
        self.client.force_login(self.user)

        # Test Action
        response = self.client.get(url)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_my_belt_timer_should_403(self):
        """
        Test should return 403 Forbidden when user lacks permissions.
        """
        # Test Data
        BeltTimerFactory(owner=self.user)
        user_no_permission = UserMainFactory(permissions__=[])
        url = reverse(
            f"{API_URL}:get_my_belt_timer",
            kwargs={"character_id": self.user.profile.main_character.character_id},
        )
        self.client.force_login(user_no_permission)

        # Test Action
        response = self.client.get(url)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_get_belt_timers_should_200(self):
        """
        Test should return 200 OK when user has permissions and resource exists.
        """
        # Test Data
        url = reverse(f"{API_URL}:get_belt_timers")
        self.client.force_login(self.user)

        # Test Action
        response = self.client.get(url)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)


class TestSnapshotApiEndpoints(BeltRadarTestCase):
    """Test Snapshot API Endpoints."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_get_snapshot_should_200(self):
        """
        Test should return 200 OK when user has permissions and resource exists.
        """
        # Test Data
        snapshot = BeltSnapshotFactory(recorded_by=self.user)
        url = reverse(
            f"{API_URL}:get_snapshot", kwargs={"public_id": snapshot.session.public_id}
        )
        self.client.force_login(self.user)

        # Test Action
        response = self.client.get(url)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.json()["snapshot"]["identifier"], str(snapshot.identifier)
        )

    def test_get_snapshot_should_403(self):
        """
        Test should return 403 Forbidden when user lacks permissions.
        """
        # Test Data
        snapshot = BeltSnapshotFactory(recorded_by=self.user)
        BeltSurveyEntryFactory(snapshot=snapshot)
        user_no_permission = UserMainFactory(permissions__=[])
        url = reverse(
            f"{API_URL}:get_snapshot", kwargs={"public_id": snapshot.session.public_id}
        )
        self.client.force_login(user_no_permission)

        # Test Action
        response = self.client.get(url)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_get_snapshot_should_404(self):
        """
        Test should return 404 Not Found when resource does not exist.
        """
        # Test Data
        url = reverse(f"{API_URL}:get_snapshot", kwargs={"public_id": "nonexistent"})
        self.client.force_login(self.user)

        # Test Action
        response = self.client.get(url)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class TestApiEndpointsPost(BeltRadarTestCase):
    """Test API Endpoints for POST requests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_add_belt_timer_should_200(self):
        """
        Test should return 200 OK when user has permissions and data is valid.
        """
        # Test Data
        url = reverse(f"{API_URL}:add_belt_timer")
        self.client.force_login(self.user)
        payload = {
            "belt_id": 12345,
            "belt_name": "Test Belt",
            "belt_type": "asteroid_belt",
            "belt_size": "large",
            "is_public": "false",
        }

        # Test Action
        response = self.client.post(
            url, data=json.dumps(payload), content_type="application/json"
        )

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_add_belt_timer_should_403(self):
        """
        Test should return 403 Forbidden when user lacks permissions.
        """
        # Test Data
        url = reverse(f"{API_URL}:add_belt_timer")
        user_no_permission = UserMainFactory(permissions__=[])
        self.client.force_login(user_no_permission)

        # Test Action
        response = self.client.post(
            url, data=json.dumps({}), content_type="application/json"
        )

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_add_belt_timer_should_400(self):
        """
        Test should return 400 Bad Request when data is invalid.
        """
        # Test Data
        url = reverse(f"{API_URL}:add_belt_timer")
        self.client.force_login(self.user)
        payload = {
            "belt_id": None,  # Invalid data
            "belt_name": "",
            "belt_type": "invalid_type",
            "belt_size": "invalid_size",
            "is_public": "not_a_boolean",
        }

        # Test Action
        response = self.client.post(
            url, data=json.dumps(payload), content_type="application/json"
        )

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_add_session_belt_timer_should_200(self):
        """
        Test should return 200 OK when user has permissions and data is valid.
        """
        # Test Data
        session = BeltSessionFactory(owner=self.user)
        snapshot = BeltSnapshotFactory(session=session, recorded_by=self.user)
        BeltSurveyEntryFactory(
            snapshot=snapshot,
            eve_type=ItemTypeFactory(name="Arkonor"),
        )
        url = reverse(
            f"{API_URL}:add_session_belt_timer", kwargs={"public_id": session.public_id}
        )
        self.client.force_login(self.user)
        payload = {
            "public_id": session.public_id,
        }

        # Test Action
        response = self.client.post(
            url, data=json.dumps(payload), content_type="application/json"
        )

        # Expected Result
        belt_timer = BeltTimer.objects.filter(owner=self.user, session=session).first()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(belt_timer.session, session)

    def test_add_session_belt_timer_should_403(self):
        """
        Test should return 403 Forbidden when user lacks permissions.
        """
        # Test Data
        session = BeltSessionFactory(owner=self.user)
        url = reverse(
            f"{API_URL}:add_session_belt_timer", kwargs={"public_id": session.public_id}
        )
        user_no_permission = UserMainFactory(permissions__=[])
        self.client.force_login(user_no_permission)
        payload = {
            "public_id": session.public_id,
        }

        # Test Action
        response = self.client.post(
            url, data=json.dumps(payload), content_type="application/json"
        )

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_add_session_belt_timer_should_404(self):
        """
        Test should return 404 Not Found when resource does not exist.
        """
        # Test Data
        url = reverse(
            f"{API_URL}:add_session_belt_timer", kwargs={"public_id": "nonexistent"}
        )
        self.client.force_login(self.user)
        payload = {
            "public_id": "nonexistent",
        }

        # Test Action
        response = self.client.post(
            url, data=json.dumps(payload), content_type="application/json"
        )

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_add_session_belt_timer_should_400(self):
        """
        Test should return 400 Bad Request when ore data is invalid.
        """
        # Test Data
        session = BeltSessionFactory(owner=self.user)
        snapshot = BeltSnapshotFactory(session=session, recorded_by=self.user)
        BeltSurveyEntryFactory(
            snapshot=snapshot,
            eve_type=ItemTypeFactory(name="Test Ore"),
        )
        url = reverse(
            f"{API_URL}:add_session_belt_timer",
            kwargs={"public_id": snapshot.session.public_id},
        )
        self.client.force_login(self.user)
        payload = {
            "public_id": snapshot.session.public_id,
        }

        # Test Action
        response = self.client.post(
            url, data=json.dumps(payload), content_type="application/json"
        )

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_delete_belt_timer_should_200(self):
        """
        Test should return 200 OK when user has permissions and resource exists.
        """
        # Test Data
        timer = BeltTimerFactory(owner=self.user)
        url = reverse(f"{API_URL}:delete_belt_timer", kwargs={"timer_id": timer.id})
        self.client.force_login(self.user)

        # Test Action
        response = self.client.post(
            url, data=json.dumps({}), content_type="application/json"
        )

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_delete_belt_timer_should_403(self):
        """
        Test should return 403 Forbidden when user lacks permissions.
        """
        # Test Data
        timer = BeltTimerFactory(owner=self.user)
        url = reverse(f"{API_URL}:delete_belt_timer", kwargs={"timer_id": timer.id})
        user_no_permission = UserMainFactory(permissions__=[])
        self.client.force_login(user_no_permission)

        # Test Action
        response = self.client.post(
            url, data=json.dumps({}), content_type="application/json"
        )

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_delete_belt_timer_should_404(self):
        """
        Test should return 404 Not Found when resource does not exist.
        """
        # Test Data
        url = reverse(f"{API_URL}:delete_belt_timer", kwargs={"timer_id": 9999})
        self.client.force_login(self.user)

        # Test Action
        response = self.client.post(
            url, data=json.dumps({}), content_type="application/json"
        )

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class TestApiSnapshotEndpointsPost(BeltRadarTestCase):
    """Test Snapshot API Endpoints for POST requests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_delete_snapshot_should_200(self):
        """
        Test should return 200 OK when user has permissions and resource exists.
        """
        # Test Data
        snapshot = BeltSnapshotFactory(session__owner=self.user)
        url = reverse(
            f"{API_URL}:delete_snapshot",
            kwargs={
                "public_id": snapshot.session.public_id,
                "identifier": snapshot.identifier,
            },
        )
        self.client.force_login(self.user)

        # Test Action
        response = self.client.post(
            url, data=json.dumps({}), content_type="application/json"
        )

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_delete_snapshot_should_403(self):
        """
        Test should return 403 Forbidden when user lacks permissions.
        """
        # Test Data
        snapshot = BeltSnapshotFactory(session__owner=self.user)
        url = reverse(
            f"{API_URL}:delete_snapshot",
            kwargs={
                "public_id": snapshot.session.public_id,
                "identifier": snapshot.identifier,
            },
        )
        user_no_permission = UserMainFactory(permissions__=[])
        self.client.force_login(user_no_permission)

        # Test Action
        response = self.client.post(
            url, data=json.dumps({}), content_type="application/json"
        )

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_delete_snapshot_should_404(self):
        """
        Test should return 404 Not Found when resource does not exist.
        """
        # Test Data
        url = reverse(
            f"{API_URL}:delete_snapshot",
            kwargs={"public_id": "nonexistent", "identifier": "nonexistent"},
        )
        self.client.force_login(self.user)

        # Test Action
        response = self.client.post(
            url, data=json.dumps({}), content_type="application/json"
        )

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_add_snapshot_should_200(self):
        """
        Test should return 200 OK when user has permissions and resource can be added.
        """
        # Test Data
        ItemTypeFactory(name="Dark Ochre IV-Grade")
        ItemTypeFactory(name="Gneiss IV-Grade")
        session = BeltSessionFactory(owner=self.user)
        url = reverse(
            f"{API_URL}:add_snapshot", kwargs={"public_id": session.public_id}
        )
        self.client.force_login(self.user)
        payload = {
            "raw_data": "Dark Ochre IV-Grade*\t1\xa0192\t9\xa0536 m3\t3\xa0990\xa0000,00 ISK\t450 km\nGneiss IV-Grade*\t1\xa0040\t5\xa0200 m3\t1\xa0860\xa0000,00 ISK\t501 km\nGneiss IV-Grade*\t990\t4\xa0950 m3\t1\xa0770\xa0000,00 ISK\t508 km\n"
        }

        # Test Action
        response = self.client.post(
            url, data=json.dumps(payload), content_type="application/json"
        )

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_add_snapshot_should_403(self):
        """
        Test should return 403 Forbidden when user lacks permissions.
        """
        # Test Data
        session = BeltSessionFactory(owner=self.user)
        url = reverse(
            f"{API_URL}:add_snapshot", kwargs={"public_id": session.public_id}
        )
        user_no_permission = UserMainFactory(permissions__=[])
        self.client.force_login(user_no_permission)

        payload = {"raw_data": ""}

        # Test Action
        response = self.client.post(
            url, data=json.dumps(payload), content_type="application/json"
        )

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_add_snapshot_should_404(self):
        """
        Test should return 404 Not Found when the session does not exist.
        """
        # Test Data
        url = reverse(f"{API_URL}:add_snapshot", kwargs={"public_id": "nonexistent"})
        self.client.force_login(self.user)

        payload = {"raw_data": ""}

        # Test Action
        response = self.client.post(
            url, data=json.dumps(payload), content_type="application/json"
        )

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_add_snapshot_should_400(self):
        """
        Test should return 400 Bad Request when the payload is invalid.
        """
        # Test Data
        session = BeltSessionFactory(owner=self.user)
        url = reverse(
            f"{API_URL}:add_snapshot", kwargs={"public_id": session.public_id}
        )
        self.client.force_login(self.user)

        payload = {"raw_data": None}

        # Test Action
        response = self.client.post(
            url, data=json.dumps(payload), content_type="application/json"
        )

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)


class TestApiSessionEndpointsPost(BeltRadarTestCase):
    """Test Snapshot API Endpoints for POST requests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_create_session_should_200(self):
        """
        Test should return 200 OK when a session is successfully created.
        """
        # Test Data
        url = reverse(f"{API_URL}:add_session")
        self.client.force_login(self.user)

        payload = {"name": "Test Session", "is_public": True}

        # Test Action
        response = self.client.post(
            url, data=json.dumps(payload), content_type="application/json"
        )

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_session_should_403(self):
        """
        Test should return 403 Forbidden when the user is not authorized to create a session.
        """
        # Test Data
        url = reverse(f"{API_URL}:add_session")
        user_no_permission = UserMainFactory(permissions__=[])
        self.client.force_login(user_no_permission)  # Ensure the user is not logged in

        payload = {"name": "Test Session", "is_public": True}

        # Test Action
        response = self.client.post(
            url, data=json.dumps(payload), content_type="application/json"
        )

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_create_session_should_400(self):
        """
        Test should return 400 Bad Request when the payload is invalid.
        """
        # Test Data
        url = reverse(f"{API_URL}:add_session")
        self.client.force_login(self.user)

        payload = {"name": ""}

        # Test Action
        response = self.client.post(
            url, data=json.dumps(payload), content_type="application/json"
        )

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
