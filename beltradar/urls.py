"""App URLs"""

# Django
from django.urls import path, re_path

# AA Belt Radar
from beltradar import views
from beltradar.api import api

app_name: str = "beltradar"  # pylint: disable=invalid-name

urlpatterns = [
    path("", views.index, name="index"),
    # -- API System
    re_path(r"^api/", api.urls),
]
