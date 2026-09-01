"""Helper choices for the Beltradar models."""

# Django
from django.db import models


class BeltTypeChoice(models.TextChoices):
    """Choices for the belt type."""

    ASTEROID_BELT = "asteroid_belt", "Asteroid Belt"
    ICE_BELT = "ice_belt", "Ice Belt"
    MERCOXIT_BELT = "mercoxit", "Mercoxit Belt"
    ARRAY_BELT = "array_belt", "Array Belt"


class BeltSizeChoice(models.TextChoices):
    """Choices for the belt size."""

    SMALL = "small", "Small"
    MEDIUM = "medium", "Medium"
    LARGE = "large", "Large"
    ENORMOUS = "enormous", "Enormous"
    COLOSSAL = "colossal", "Colossal"
    ICE = "ice", "Ice"
