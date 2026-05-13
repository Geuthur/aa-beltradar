"""Template for a TestView class."""

# Standard Library
from http import HTTPStatus

# Django
from django.urls import reverse

# AA Example
from example.tests import ExampleTestCase
from example.tests.testdata.utils import create_user_from_evecharacter
from example.views import index


class TestViews(ExampleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    # def test_view(self):
    #    request = self.factory.get(reverse("example:index"))
    #    request.user = self.user
    #    response = index(request)
    #    self.assertEqual(response.status_code, HTTPStatus.OK)
