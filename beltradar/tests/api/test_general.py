# Standard Library
import json
from http import HTTPStatus

# Django
from django.urls import reverse

# AA Belt Radar
from beltradar.models.beltradar import UserSettings
from beltradar.tests import AuthTestCase
from beltradar.tests.testdata.beltradar import UserMainFactory

API_URL = "beltradar:api"


class TestGeneralApiEndpoints(AuthTestCase):
    """Test the menu, user and settings endpoints."""

    def test_get_menu_should_return_left_and_right_links(self):
        """The menu follows the contract of aa-geuthur-react."""
        # Test Data
        self.client.force_login(self.user)

        # Test Action
        response = self.client.get(reverse(f"{API_URL}:get_menu"))

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        self.assertEqual(
            [link["name"] for link in data["left_links"]],
            ["Belt Radar", "My Sessions", "Settings"],
        )
        self.assertEqual(data["right_links"], [])
        self.assertIn("create_session", data["modals"])

    def test_get_user_should_return_contract_fields(self):
        """The user endpoint delivers the character, corporation and admin flag."""
        # Test Data
        self.client.force_login(self.user)
        main = self.user.profile.main_character

        # Test Action
        response = self.client.get(reverse(f"{API_URL}:get_user"))

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        self.assertEqual(data["user_id"], self.user.id)
        self.assertEqual(data["character_id"], main.character_id)
        self.assertEqual(data["corporation_id"], main.corporation_id)
        self.assertEqual(data["corporation_name"], main.corporation_name)
        self.assertFalse(data["is_admin"])

    def test_get_user_should_flag_superuser_as_admin(self):
        """is_admin is the superuser flag."""
        # Test Data
        self.client.force_login(self.superuser)

        # Test Action
        response = self.client.get(reverse(f"{API_URL}:get_user"))

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.json()["is_admin"])

    def test_get_user_should_403(self):
        """Users without the basic permission are rejected."""
        # Test Data
        self.client.force_login(UserMainFactory(permissions__=[]))

        # Test Action
        response = self.client.get(reverse(f"{API_URL}:get_user"))

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertIn("error", response.json())

    def test_get_user_settings_should_return_default(self):
        """New users have notifications enabled."""
        # Test Data
        self.client.force_login(self.user)

        # Test Action
        response = self.client.get(reverse(f"{API_URL}:get_user_settings"))

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json(), {"disable_notifications": False})

    def test_update_user_settings_should_save(self):
        """PUT settings stores the flag and returns it."""
        # Test Data
        self.client.force_login(self.user)

        # Test Action
        response = self.client.put(
            reverse(f"{API_URL}:update_user_settings"),
            data=json.dumps({"disable_notifications": True}),
            content_type="application/json",
        )

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json(), {"disable_notifications": True})
        self.assertTrue(UserSettings.objects.get(user=self.user).disable_notifications)

    def test_update_user_settings_should_403(self):
        """Users without the basic permission cannot change settings."""
        # Test Data
        user = UserMainFactory(permissions__=[])
        self.client.force_login(user)

        # Test Action
        response = self.client.put(
            reverse(f"{API_URL}:update_user_settings"),
            data=json.dumps({"disable_notifications": True}),
            content_type="application/json",
        )

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertFalse(UserSettings.objects.filter(user=user).exists())
