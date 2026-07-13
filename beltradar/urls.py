"""App URLs"""

# Django
from django.urls import path, re_path

# AA Belt Radar
from beltradar import views
from beltradar.api import api

app_name: str = "beltradar"  # pylint: disable=invalid-name

urlpatterns = [
    path("", views.index, name="index"),
    path("survey/create-session/", views.create_session, name="create_session"),
    path("survey/my-sessions/", views.view_my_sessions, name="view_my_sessions"),
    path(
        "survey/my-sessions/<int:character_id>/",
        views.view_my_sessions,
        name="view_my_sessions",
    ),
    path("survey/user-sessions/", views.view_user_sessions, name="view_user_sessions"),
    path("survey/<str:public_id>/view/", views.view_session, name="view_session"),
    # -- API System
    re_path(r"^api/", api.urls),
]
