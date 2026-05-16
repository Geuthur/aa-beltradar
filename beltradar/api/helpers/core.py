# Django
from django.core.exceptions import ObjectDoesNotExist

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# AA Belt Radar
from beltradar import __title__, models
from beltradar.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


def get_owner_or_none(
    request, character_id
) -> tuple[bool, models.BeltSurveySession | None]:
    """Get Character and check permissions"""
    perms = True

    try:
        survey_session = models.BeltSurveySession.objects.get(
            owner__profile__main_character__character_id=character_id
        )
    except ObjectDoesNotExist:
        return False, None
    except ValueError:
        return None, None

    # check access
    visible = models.BeltSurveySession.objects.visible_eve_characters(request.user)
    if survey_session.owner.profile.main_character not in visible:
        perms = False
    return perms, survey_session


def get_public_id_or_none(
    request, public_id
) -> tuple[bool, models.BeltSurveySession | None]:
    """Get Character and check permissions"""
    perms = True

    try:
        survey_session = models.BeltSurveySession.objects.get(public_id=public_id)
    except ObjectDoesNotExist:
        return False, None
    except ValueError:
        return None, None

    # check access
    visible = models.BeltSurveySession.objects.visible_eve_characters(request.user)
    if survey_session.owner.profile.main_character not in visible:
        perms = False
    return perms, survey_session
