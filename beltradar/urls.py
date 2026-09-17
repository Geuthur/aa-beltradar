"""App URLs"""

# Django
from django.urls import re_path

# AA Belt Radar
from beltradar import views
from beltradar.api import api

app_name: str = "beltradar"  # pylint: disable=invalid-name

urlpatterns = [
    # -- Catch-all / React Frontend Routing
    re_path(r"^(?P<character_id>\d+)/", views.react_base, name="react_base"),
    re_path(r"^(?!api/).*$", views.react_base, name="react_base"),
    # -- API System
    re_path(r"^api/", api.urls),
]
