"""TestView class."""

# Standard Library
from http import HTTPStatus

# Third Party
from evesde_factory.allianceauth import UserFactory

# Django
from django.conf import settings
from django.shortcuts import resolve_url
from django.urls import resolve, reverse

# AA Belt Radar
from beltradar import urls, views
from beltradar.auth_hooks import BeltRadarMenuItem
from beltradar.tests import AuthTestCase
from beltradar.tests.testdata.beltradar import UserMainFactory

MODULE_PATH = "beltradar.views."


class TestViewAccess(AuthTestCase):
    """The React page requires login and basic_access on every path."""

    # Paths the catch-all serves: index, a frontend route, and paths with a
    # leading number (formerly a separate route with `character_id`).
    PAGE_PATHS = ["", "my-belt-radar/123/", "123/", "123/settings/", "123"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.base_url = reverse("beltradar:react_base")

    def test_react_base_should_render_view(self):
        # given
        request = self.factory.get(self.base_url)
        request.user = self.user
        # when
        response = views.react_base(request)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "aa-beltradar-root")
        self.assertNotIn("character_id", response.content.decode())

    def test_react_base_should_return_page_with_basic_access(self):
        self.client.force_login(self.user)
        for path in self.PAGE_PATHS:
            with self.subTest(path=path):
                response = self.client.get(f"{self.base_url}{path}")
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertContains(response, "aa-beltradar-root")

    def test_react_base_should_redirect_unauthenticated_user_to_login(self):
        for path in self.PAGE_PATHS:
            with self.subTest(path=path):
                response = self.client.get(f"{self.base_url}{path}")
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                self.assertIn(resolve_url(settings.LOGIN_URL), response.url)

    def test_react_base_should_not_return_page_without_basic_access(self):
        """Other permissions of the app do not open the page either."""
        for permissions in (
            [],
            ["beltradar.manage_access"],
            ["beltradar.admin_access"],
        ):
            self.client.force_login(UserMainFactory(permissions=permissions))
            for path in self.PAGE_PATHS:
                with self.subTest(permissions=permissions, path=path):
                    response = self.client.get(f"{self.base_url}{path}")
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)
                    self.assertIn(resolve_url(settings.LOGIN_URL), response.url)
                    self.assertNotIn(b"aa-beltradar-root", response.content)

    def test_react_base_should_not_return_page_for_other_methods_without_access(self):
        self.client.force_login(UserMainFactory(permissions=[]))
        for method in ("post", "put", "head", "options"):
            with self.subTest(method=method):
                response = getattr(self.client, method)(f"{self.base_url}123/")
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_react_base_should_not_fail_for_user_without_main_character(self):
        """The view itself no longer needs a main character."""
        # given
        user = UserFactory(permissions=["beltradar.basic_access"])
        self.assertIsNone(user.profile.main_character)
        request = self.factory.get(self.base_url)
        request.user = user
        # when
        response = views.react_base(request)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "aa-beltradar-root")

    def test_react_base_should_redirect_user_without_main_character(self):
        """Alliance Auth wraps all app urls with `main_character_required`."""
        # given
        user = UserFactory(permissions=["beltradar.basic_access"])
        self.client.force_login(user)
        for path in self.PAGE_PATHS:
            with self.subTest(path=path):
                # when
                response = self.client.get(f"{self.base_url}{path}")
                # then
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                self.assertNotIn(b"aa-beltradar-root", response.content)

    def test_react_base_should_be_the_only_page_route(self):
        """Every route except the API resolves to the protected view, without arguments."""
        for path in self.PAGE_PATHS:
            with self.subTest(path=path):
                match = resolve(f"{self.base_url}{path}")
                self.assertEqual(match.view_name, "beltradar:react_base")
                self.assertEqual(match.kwargs, {})
        self.assertNotEqual(
            resolve(f"{self.base_url}api/menu/").view_name, "beltradar:react_base"
        )
        page_routes = [
            pattern
            for pattern in urls.urlpatterns
            if getattr(pattern, "name", None) == "react_base"
        ]
        self.assertEqual(len(page_routes), 1)
        self.assertEqual(len(urls.urlpatterns), 2)


class TestMenuHook(AuthTestCase):
    """The menu entry follows basic_access, checked through the GeneralManager."""

    def test_render_should_show_entry_with_basic_access(self):
        request = self.factory.get("/")
        request.user = self.user
        self.assertNotEqual(BeltRadarMenuItem().render(request), "")

    def test_render_should_hide_entry_without_basic_access(self):
        request = self.factory.get("/")
        request.user = UserMainFactory(permissions=[])
        self.assertEqual(BeltRadarMenuItem().render(request), "")
