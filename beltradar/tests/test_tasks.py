# Standard Library
from unittest.mock import patch

# Third Party
import pook

# Django
from django.test import override_settings
from django.utils import timezone

# AA Belt Radar
from beltradar import __app_name__, tasks
from beltradar.models import BeltSurveySession, BeltTimer
from beltradar.tests import BeltRadarTestCase
from beltradar.tests.testdata.beltradar import BeltTimerFactory

TASK_PATH = "beltradar.tasks"


@override_settings(
    CELERY_ALWAYS_EAGER=True,
    CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
    BELT_RADAR_WEBHOOK_URL="https://discord.com/api/webhooks/1337/abc123",
)
class TestUpdateAllBeltRadar(BeltRadarTestCase):
    """Test the update_all_belt_radar task."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.session = BeltSurveySession.objects.create(
            name="Test Session", owner=cls.user
        )

    @patch(TASK_PATH + ".send_user_notification.delay")
    @patch(TASK_PATH + ".logger")
    @pook.on
    def test_should_update_all_belt_radar_should_trigger_notifications(
        self,
        mock_logger,
        mock_send_user_notification,
    ):
        """
            Test should start update_belt_radar_session for each BeltSurveySession.
        :return:
        :rtype:
        """
        # Test Data

        # Mock the webhook response to simulate a successful notification
        pook.post(
            "https://discord.com/api/webhooks/1337/abc123",
            reply=200,
            response_json={
                "application_id": None,
                "avatar": "",
                "channel_id": "",
                "guild_id": "",
                "id": "",
                "name": "Belt Notifier",
                "type": 1,
                "token": "",
                "url": "https://discord.com/api/webhooks/1337/abc123",
            },
        )

        # Create a BeltTimer that is expired and public, and has not sent a notification yet
        belt_timer = BeltTimerFactory(
            owner=self.user,
            public=True,
            sent_notification=False,
        )
        expired_eta = timezone.now() - timezone.timedelta(days=2)
        BeltTimer.objects.filter(pk=belt_timer.pk).update(
            eta=expired_eta,
            sent_notification=False,
        )
        belt_timer.refresh_from_db()

        # Test Action
        tasks.update_all_belt_radar()

        # Expected Result
        mock_send_user_notification.assert_called_once()
        mock_logger.info.assert_called()

    @patch(TASK_PATH + ".EveMarketPrice.objects.update_from_esi", return_value=42)
    def test_should_update_market_prices(self, mock_update_from_esi):
        """
            Test should update market prices when update_market_prices is called.
        :return:
        :rtype:
        """
        # Test Action
        tasks.update_market_prices()

        # Expected Result
        self.assertTrue(mock_update_from_esi.called)
        self.assertEqual(mock_update_from_esi.call_count, 1)
        mock_update_from_esi.assert_called_once_with()
