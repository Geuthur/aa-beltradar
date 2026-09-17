"""TestView class."""

# Standard Library
from http import HTTPStatus

# Django
from django.urls import reverse

# AA Belt Radar
from beltradar import views
from beltradar.tests import BeltRadarTestCase

MODULE_PATH = "beltradar.views."


class TestViewAccess(BeltRadarTestCase):
    """Test General Belt Radar View Access."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_react_base_default_character(self):
        """
        Test should render react view with user's main character.
        """
        # given
        request = self.factory.get(reverse("beltradar:react_base"))
        request.user = self.user
        # when
        response = views.react_base(request)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "aa-beltradar-root")

    def test_react_base_with_character_id(self):
        """
        Test should render react view with specific character ID.
        """
        # given
        character_id = 987654321
        request = self.factory.get(
            reverse("beltradar:react_base", kwargs={"character_id": character_id})
        )
        request.user = self.user
        # when
        response = views.react_base(request, character_id=character_id)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "aa-beltradar-root")

    def test_react_base_client_authenticated(self):
        """
        Test should return 200 OK for logged-in user via test client.
        """
        self.client.force_login(self.user)
        response = self.client.get(reverse("beltradar:react_base"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "aa-beltradar-root")

    def test_react_base_client_unauthenticated(self):
        """
        Test should redirect unauthenticated user to login.
        """
        response = self.client.get(reverse("beltradar:react_base"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
