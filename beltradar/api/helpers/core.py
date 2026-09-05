# Django
from django.core.exceptions import ObjectDoesNotExist

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# AA Belt Radar
from beltradar import __title__, models
from beltradar.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


def get_session_or_none(
    request, public_id
) -> tuple[bool | None, models.BeltSurveySession | None]:
    """Get Session and check permissions"""
    perms = True

    try:
        session = models.BeltSurveySession.objects.get(public_id=public_id)
    except (ObjectDoesNotExist, ValueError):
        return None, None

    # check access
    visible = models.BeltSurveySession.objects.visible_to(request.user)
    if session not in visible:
        perms = False
    return perms, session


def get_manage_session_or_none(
    request, public_id
) -> tuple[bool | None, models.BeltSurveySession | None]:
    """Get Session and check permissions"""
    perms = True

    try:
        session = models.BeltSurveySession.objects.get(public_id=public_id)
    except (ObjectDoesNotExist, ValueError):
        return None, None

    # check access
    visible = models.BeltSurveySession.objects.manage_to(request.user)
    if session not in visible:
        perms = False
    return perms, session


def get_belt_timer_or_none(
    request, character_id: int
) -> tuple[bool | None, models.BeltTimer | None]:
    """Get Belt Timer and check permissions"""
    perms = True
    try:
        timer = models.BeltTimer.objects.filter(
            owner__profile__main_character__character_id=character_id
        ).first()
        if not timer:
            print("No timer found for character_id:", character_id)
            return None, None
    except ValueError:
        return None, None

    # check access
    visible = models.BeltTimer.objects.visible_to(request.user)
    if timer not in visible:
        perms = False
    return perms, timer


def get_manage_belt_timer_or_none(
    request, timer_pk: int
) -> tuple[bool | None, models.BeltTimer | None]:
    """Get Belt Timer and check permissions"""
    perms = True

    try:
        timer = models.BeltTimer.objects.get(pk=timer_pk)
    except (ObjectDoesNotExist, ValueError):
        return None, None

    # check access
    visible = models.BeltTimer.objects.manage_to(request.user)
    if timer not in visible:
        perms = False
    return perms, timer
