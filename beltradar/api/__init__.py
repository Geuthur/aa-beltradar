# Third Party
from ninja import NinjaAPI
from ninja.security import django_auth

# Django
from django.conf import settings

# AA Belt Radar
from beltradar import __title__
from beltradar.api import survey, timer

api = NinjaAPI(
    title="Belt Radar API",
    version="0.1.0",
    urls_namespace="beltradar:api",
    auth=django_auth,
    openapi_url=settings.DEBUG and "/openapi.json" or "",
)


def setup(ninja_api):
    survey.BeltRadarSurveyApiEndpoints(ninja_api)
    timer.BeltRadarBeltTimerApiEndpoints(ninja_api)


# Initialize API endpoints
setup(api)
