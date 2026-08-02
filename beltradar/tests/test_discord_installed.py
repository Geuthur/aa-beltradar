# Django
from django.test import modify_settings

# AA Belt Radar
from beltradar.tests import NoSocketsTestCase
from beltradar.thirdparty.discord import (
    allianceauth_discordbot_installed,
    discordnotify_installed,
)


class TestModulesInstalled(NoSocketsTestCase):
    @modify_settings(INSTALLED_APPS={"remove": "aadiscordbot"})
    def test_allianceauth_discordbot_installed_should_return_false(self):
        self.assertFalse(allianceauth_discordbot_installed())

    @modify_settings(INSTALLED_APPS={"append": "aadiscordbot"})
    def test_allianceauth_discordbot_installed_should_return_true(self):
        self.assertTrue(allianceauth_discordbot_installed())

    @modify_settings(INSTALLED_APPS={"remove": "discordnotify"})
    def test_aa_discordnotify_installed_should_return_false(self):
        self.assertFalse(discordnotify_installed())

    @modify_settings(INSTALLED_APPS={"append": "discordnotify"})
    def test_aa_discordnotify_installed_should_return_true(self):
        self.assertTrue(discordnotify_installed())
