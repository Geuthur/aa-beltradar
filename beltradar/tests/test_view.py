"""Template for a TestView class."""

# Standard Library
from http import HTTPStatus

# Django
from django.urls import reverse

# AA Beltradar
from beltradar.tests import BeltRadarTestCase
from beltradar.tests.testdata.utils import create_user_from_evecharacter
from beltradar.views import index


class TestViews(BeltRadarTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_view(self):
        request = self.factory.get(reverse("beltradar:index"))
        request.user = self.user
        response = index(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)
