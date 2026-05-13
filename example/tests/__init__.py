# Standard Library
import socket
from unittest.mock import Mock

# Django
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.handlers.wsgi import WSGIRequest
from django.test import RequestFactory, TestCase

# AA Example
from example.tests.testdata.integrations.allianceauth import load_allianceauth
from example.tests.testdata.utils import create_user_from_evecharacter


class SocketAccessError(Exception):
    """Error raised when a test script accesses the network"""


class NoSocketsTestCase(TestCase):
    """Variation of Django's TestCase class that prevents any network use.

    Example:

        .. code-block:: python

            class TestMyStuff(BaseTestCase):
                def test_should_do_what_i_need(self): ...

    """

    @classmethod
    def setUpClass(cls):
        cls.socket_original = socket.socket
        socket.socket = cls.guard
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        socket.socket = cls.socket_original
        return super().tearDownClass()

    @staticmethod
    def guard(*args, **kwargs):
        raise SocketAccessError("Attempted to access network")


class ExampleTestCase(NoSocketsTestCase):
    """
    Preloaded Testcase class for Example tests without Network access.

    Pre-Load:
        * Alliance Auth Characters, Corporation, Alliance Data
        * Taken User IDs: 1001

    Available Request Factory:
        `self.factory`

    Available test users:
        * `user` User with standard Example access.
            * 'example.basic_access' Permission
            * Character ID 1001
            * Corporation ID 2001
            * Alliance ID 3001

    Example:
        .. code-block:: python

            class TestMyExampleStuff(ExampleTestCase):
                def test_should_do_what_i_need(self):
                    user = self.user
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Initialize Alliance Auth test data
        load_allianceauth()

        # Request Factory
        cls.factory = RequestFactory()

        # User with Standard Access - Corporation 2001
        cls.user, cls.user_character = create_user_from_evecharacter(
            character_id=1001,
            permissions=["example.basic_access"],
        )

    def _middleware_process_request(self, request: WSGIRequest):
        """Helper method to process middleware for a request."""
        session_middleware = SessionMiddleware(Mock())
        session_middleware.process_request(request)
        message_middleware = MessageMiddleware(Mock())
        message_middleware.process_request(request)
