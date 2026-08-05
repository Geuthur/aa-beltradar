# Standard Library
import json
from http import HTTPStatus

# Django
from django.urls import reverse

# AA Belt Radar
from beltradar.tests import BeltRadarTestCase
from beltradar.tests.testdata.beltradar import (
    BeltSessionFactory,
    BeltSurveyEntryFactory,
    BeltTimerFactory,
    UserMainFactory,
)

MODULE_PATH = "beltradar.api.helpers."
API_URL = "beltradar:api"


class TestApiEndpoints(BeltRadarTestCase):
    """Test API Endpoints."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_get_sessions_should_403(self):
        """
        Test should return 403 Forbidden when user lacks permissions.
        """
        # Test Data
        user_no_permission = UserMainFactory(permissions__=[])
        url = reverse(f"{API_URL}:get_survey_session", kwargs={"public_id": "1"})
        self.client.force_login(user_no_permission)

        # Test Action
        response = self.client.get(url)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_get_survey_session_should_404(self):
        """
        Test should return 404 Not Found when resource does not exist.
        """
        # Test Data
        url = reverse(
            f"{API_URL}:get_survey_session", kwargs={"public_id": "nonexistent"}
        )
        self.client.force_login(self.user)

        # Test Action
        response = self.client.get(url)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_get_survey_session_should_200(self):
        """
        Test should return 200 OK when user has permissions and resource exists.
        """
        # Test Data
        session = BeltSessionFactory(owner=self.user)
        url = reverse(
            f"{API_URL}:get_survey_session", kwargs={"public_id": session.public_id}
        )
        self.client.force_login(self.user)

        # Test Action
        response = self.client.get(url)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)

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

    def test_get_sessions_should_200(self):
        """
        Test should return 200 OK when user has permissions and resource exists.
        """
        # Test Data
        BeltSessionFactory(owner=self.user)
        BeltSessionFactory(owner=self.user)
        url = reverse(f"{API_URL}:get_sessions")
        self.client.force_login(self.user)

        # Test Action
        response = self.client.get(url)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_survey_entry_should_200(self):
        """
        Test should return 200 OK when user has permissions and resource exists.
        """
        # Test Data
        session = BeltSessionFactory(owner=self.user)
        survey_entry = BeltSurveyEntryFactory(session=session, recorded_by=self.user)
        url = reverse(
            f"{API_URL}:get_survey_entry", kwargs={"public_id": session.public_id}
        )
        self.client.force_login(self.user)

        # Test Action
        response = self.client.get(url)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.json()["session"]["public_id"], str(session.public_id)
        )
        self.assertEqual(
            response.json()["entries"][0]["snapshot"], survey_entry.snapshot
        )

    def test_get_survey_entry_should_403(self):
        """
        Test should return 403 Forbidden when user lacks permissions.
        """
        # Test Data
        session = BeltSessionFactory(owner=self.user)
        BeltSurveyEntryFactory(session=session, recorded_by=self.user)
        user_no_permission = UserMainFactory(permissions__=[])
        url = reverse(
            f"{API_URL}:get_survey_entry", kwargs={"public_id": session.public_id}
        )
        self.client.force_login(user_no_permission)

        # Test Action
        response = self.client.get(url)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_get_survey_entry_should_404(self):
        """
        Test should return 404 Not Found when resource does not exist.
        """
        # Test Data
        url = reverse(
            f"{API_URL}:get_survey_entry", kwargs={"public_id": "nonexistent"}
        )
        self.client.force_login(self.user)

        # Test Action
        response = self.client.get(url)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

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

    def test_get_my_belt_timer_should_404(self):
        """
        Test should return 404 Not Found when resource does not exist.
        """
        # Test Data
        url = reverse(f"{API_URL}:get_my_belt_timer", kwargs={"character_id": 1337})
        self.client.force_login(self.user)

        # Test Action
        response = self.client.get(url)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

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
