"""App URLs"""

# Django
from django.urls import re_path

# Alliance Auth
from allianceauth.authentication.decorators import decorate_url_patterns

# AA Belt Radar
from beltradar import views
from beltradar.api import api
from beltradar.api.auth import basic_access_required

app_name: str = "beltradar"  # pylint: disable=invalid-name

# Every URL of the API (endpoints, schema and docs) requires `basic_access`
api_patterns, api_app_name, api_namespace = api.urls
api_patterns = decorate_url_patterns(
    (api_patterns, api_app_name), basic_access_required
)[0]

urlpatterns = [
    # -- Catch-all / React Frontend Routing
    re_path(r"^(?!api/).*$", views.react_base, name="react_base"),
    # -- API System
    re_path(r"^api/", (api_patterns, api_app_name, api_namespace)),
]
