# Standard Library
from unittest.mock import patch

# Django
from django.test import override_settings

# AA Belt Radar
from beltradar import tasks
from beltradar.models import BeltSurveySession
from beltradar.tests import BeltRadarTestCase

TASK_PATH = "beltradar.tasks"


@override_settings(
    CELERY_ALWAYS_EAGER=True,
    CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
)
class TestUpdateAllBeltRadar(BeltRadarTestCase):
    """Test the update_all_belt_radar task."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.session = BeltSurveySession.objects.create(
            name="Test Session", owner=cls.user
        )

    @patch(TASK_PATH + ".logger")
    def test_should_update_all_belt_radar(self, mock_logger):
        """
            Test should start update_belt_radar_session for each BeltSurveySession.
        :return:
        :rtype:
        """
        # when
        tasks.update_all_belt_radar()
        # then
        self.assertTrue(mock_logger.info.called)

    @patch(TASK_PATH + ".EveMarketPrice.objects.update_from_esi", return_value=42)
    def test_should_update_market_prices(self, mock_update_from_esi):
        """
            Test should update market prices when update_market_prices is called.
        :return:
        :rtype:
        """
        tasks.update_market_prices()
        self.assertTrue(mock_update_from_esi.called)
        self.assertEqual(mock_update_from_esi.call_count, 1)
        mock_update_from_esi.assert_called_once_with()
