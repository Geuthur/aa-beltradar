"""App URLs"""

# Django
from django.urls import path, re_path

# AA Belt Radar
from beltradar import views
from beltradar.api import api

app_name: str = "beltradar"  # pylint: disable=invalid-name

urlpatterns = [
    path("", views.view_belt_radar, name="index"),
    path("user-settings/", views.view_my_settings, name="view_my_settings"),
    # -- Session Management
    path("session/", views.view_belt_radar, name="view_belt_radar"),
    path("session/<str:public_id>/view/", views.view_session, name="view_session"),
    # -- My Belt Radar
    path("my-belt-radar/", views.view_my_beltradar, name="view_my_beltradar"),
    path(
        "my-belt-radar/<int:character_id>/",
        views.view_my_beltradar,
        name="view_my_beltradar",
    ),
    # -- API System
    re_path(r"^api/", api.urls),
]
