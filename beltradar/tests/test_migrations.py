# Django
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase

# Alliance Auth
from allianceauth.authentication.models import User

MIGRATE_FROM = [("beltradar", "0013_alter_evemarketprice_adjusted_price")]
MIGRATE_TO = [("beltradar", "0015_alter_usersettings_user")]


class TestUserSettingsOneToOneMigration(TransactionTestCase):
    """Test the cleanup before `UserSettings.user` becomes a OneToOneField."""

    def setUp(self):
        super().setUp()
        self.executor = MigrationExecutor(connection)
        self.executor.migrate(MIGRATE_FROM)

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def _migrate_to_onetoone(self):
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(MIGRATE_TO)
        return executor.loader.project_state(MIGRATE_TO).apps

    def test_should_keep_newest_settings_per_user_and_remove_orphans(self):
        """
        Test should keep only the newest settings row per user and remove rows without user.

        # Test Scenario:
        1. Two users, the first with three settings rows, the second with one
        2. Two settings rows without user
        3. Migrate to the OneToOneField

        # Expected Result:
        - The first user keeps only the row with the highest primary key
        - The second user keeps his single row
        - Rows without user are removed
        """
        # Test Data
        old_apps = self.executor.loader.project_state(MIGRATE_FROM).apps
        UserSettings = old_apps.get_model("beltradar", "UserSettings")
        user_1 = User.objects.create_user("user_1")
        user_2 = User.objects.create_user("user_2")
        UserSettings.objects.create(user_id=user_1.pk, disable_notifications=False)
        UserSettings.objects.create(user_id=user_1.pk, disable_notifications=False)
        newest_user_1 = UserSettings.objects.create(
            user_id=user_1.pk, disable_notifications=True
        )
        single_user_2 = UserSettings.objects.create(user_id=user_2.pk)
        UserSettings.objects.create(user=None)
        UserSettings.objects.create(user=None)

        # Test Action
        new_apps = self._migrate_to_onetoone()

        # Expected Results
        UserSettings = new_apps.get_model("beltradar", "UserSettings")
        self.assertEqual(
            list(UserSettings.objects.order_by("pk").values_list("pk", "user_id")),
            [(newest_user_1.pk, user_1.pk), (single_user_2.pk, user_2.pk)],
        )
        self.assertTrue(
            UserSettings.objects.get(user_id=user_1.pk).disable_notifications
        )

    def test_should_migrate_without_settings(self):
        """
        Test should migrate when no settings exist.

        # Test Scenario:
        1. No settings rows
        2. Migrate to the OneToOneField

        # Expected Result:
        - Migration runs without error and no rows exist
        """
        # Test Action
        new_apps = self._migrate_to_onetoone()

        # Expected Results
        UserSettings = new_apps.get_model("beltradar", "UserSettings")
        self.assertFalse(UserSettings.objects.exists())
