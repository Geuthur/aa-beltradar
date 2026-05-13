# Third Party
from ninja import NinjaAPI
from ninja.security import django_auth

# Django
from django.conf import settings

# AA Example
from example import __title__
from example.api import character

api = NinjaAPI(
    title="Example API",
    version="0.5.0",
    urls_namespace="example:api",
    auth=django_auth,
    openapi_url=settings.DEBUG and "/openapi.json" or "",
)


def setup(ninja_api):
    character.CharacterApiEndpoints(ninja_api)


# Initialize API endpoints
setup(api)
