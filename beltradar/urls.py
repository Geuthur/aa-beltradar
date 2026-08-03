"""App URLs"""

# Django
from django.urls import path, re_path

# AA Belt Radar
from beltradar import views
from beltradar.api import api

app_name: str = "beltradar"  # pylint: disable=invalid-name

urlpatterns = [
    path("", views.view_belt_radar, name="index"),
    path("survey/user-settings/", views.view_my_settings, name="view_my_settings"),
    # -- Session Management
    path("survey/create-session/", views.create_session, name="create_session"),
    # -- Survey Management
    path("survey/my-belt-radar/", views.view_my_beltradar, name="view_my_beltradar"),
    path(
        "survey/my-belt-radar/<int:character_id>/",
        views.view_my_beltradar,
        name="view_my_beltradar",
    ),
    path("survey/belt-radar/", views.view_belt_radar, name="view_belt_radar"),
    path("survey/<str:public_id>/view/", views.view_session, name="view_session"),
    # -- Belt Timer Management
    path("belt-timer/create-timer/", views.create_belt_timer, name="create_belt_timer"),
    # -- API System
    re_path(r"^api/", api.urls),
]
