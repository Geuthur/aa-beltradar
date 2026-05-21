"""
Management command to migrate market data for Belt Radar.
"""

# Django
from django.core.management.base import BaseCommand

# AA Belt Radar
from beltradar.models import EveMarketPrice


class Command(BaseCommand):
    """
    Command to migrate market data for Belt Radar.
    """

    def _migrate_market_data(
        self,
    ):  # pylint: disable=too-many-locals, too-many-statements
        """
        Perform the migration of market data for Belt Radar.
        """

        self.stdout.write("Updating market prices from ESI...")
        count = EveMarketPrice.objects.update_from_esi()
        self.stdout.write(f"Updated market prices for {count} items.")
        self.stdout.write("Migration finished.")

    def handle(self, *args, **options):  # pylint: disable=unused-argument
        """
        Handle the command execution.
        """

        self.stdout.write("Migrating Belt Radar Market Data.")

        if input("Are you sure you want to proceed? (yes/no)?") == "yes":
            self.stdout.write("Starting migration...")
            self._migrate_market_data()
            self.stdout.write(self.style.SUCCESS("Migration complete!"))
        else:
            self.stdout.write(self.style.WARNING("Aborted."))
