"""
App Settings
"""

# Django
from django.conf import settings

# Set Naming on Auth Hook
BELT_RADAR_APP_NAME = getattr(settings, "BELT_RADAR_APP_NAME", "Belt Radar")

# Task Settings
# Global timeout for tasks in seconds to reduce task accumulation during outages.
BELT_RADAR_TASK_TIME_LIMIT = getattr(
    settings, "BELT_RADAR_TASK_TIME_LIMIT", 1200
)  # 20 minutes

# Maximum Number of Objects processed per run of DJANGO Batch Method
# Controls how many database records are inserted in a single batch operation.
# If you encounter "Got a packet bigger than 'max_allowed_packet' bytes" errors,
# reduce this value (e.g., to 250 or 100).
# Can be increased for better performance if your MySQL max_allowed_packet setting
# is configured higher (default is usually 16-64MB).
BELT_RADAR_BULK_BATCH_SIZE = getattr(settings, "BELT_RADAR_BULK_BATCH_SIZE", 500)
BELT_RADAR_WEBHOOK_URL = getattr(settings, "BELT_RADAR_WEBHOOK_URL", None)
