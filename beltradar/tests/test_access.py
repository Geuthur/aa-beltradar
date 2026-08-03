"""TestView class."""

# Standard Library
import uuid
from http import HTTPStatus

# Django
from django.http import Http404
from django.urls import reverse

# AA Belt Radar
from beltradar import views
from beltradar.models import BeltSurveySession

# AA Beltradar
from beltradar.tests import BeltRadarTestCase

MODULE_PATH = "beltradar.views."


class TestViewAccess(BeltRadarTestCase):
    """Test General Belt Radar View Access."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_index(self):
        """
        Test should render index view.
        """
        # given
        request = self.factory.get(reverse("beltradar:index"))
        request.user = self.user
        # when
        response = views.index(request)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Index")

    def test_create_session(self):
        """
        Test should render create session view.
        """
        # given
        request = self.factory.get(reverse("beltradar:create_session"))
        request.user = self.user
        # when
        response = views.create_session(request)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Create Belt Survey Session")

    def test_create_session_post(self):
        """
        Test should create session and redirect to view session.
        """
        # given
        request = self.factory.post(
            reverse("beltradar:create_session"), data={"name": "Test Session"}
        )
        request.user = self.user
        # when
        response = views.create_session(request)
        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        session = BeltSurveySession.objects.get(name="Test Session")
        self.assertEqual(
            response.url, reverse("beltradar:view_session", args=[session.public_id])
        )
        self.assertEqual(session.owner, self.user)

    def test_view_session(self):
        """
        Test should render view session view.
        """
        # given
        session = BeltSurveySession.objects.create(
            owner=self.user, public_id="test", name="Test Session"
        )
        request = self.factory.get(
            reverse("beltradar:view_session", args=[session.public_id])
        )
        request.user = self.user
        # when
        response = views.view_session(request, public_id=session.public_id)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "View Session - Test Session")

    def test_view_session_no_name(self):
        """
        Test should render view session view with public ID in title when session has no name.
        """
        # given
        session = BeltSurveySession.objects.create(owner=self.user, public_id="test")
        request = self.factory.get(
            reverse("beltradar:view_session", args=[session.public_id])
        )
        request.user = self.user
        # when
        response = views.view_session(request, public_id=session.public_id)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, f"View Session - {session.public_id}")

    def test_view_session_not_found(self):
        """
        Test should return 404 when session not found.
        """
        # given
        test_uuid = uuid.uuid4()
        request = self.factory.get(
            reverse("beltradar:view_session", kwargs={"public_id": test_uuid})
        )
        request.user = self.user
        # when
        with self.assertRaises(Http404):
            views.view_session(request, public_id=test_uuid)

    def test_view_my_beltradar(self):
        """
        Test should render view my sessions view.
        """
        # given
        request = self.factory.get(reverse("beltradar:view_my_beltradar"))
        request.user = self.user
        # when
        response = views.view_my_beltradar(request)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "My Sessions")

    def test_view_my_settings(self):
        """
        Test should render view my settings view.
        """
        # given
        request = self.factory.get(reverse("beltradar:view_my_settings"))
        request.user = self.user
        # when
        response = views.view_my_settings(request)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "My Settings")
