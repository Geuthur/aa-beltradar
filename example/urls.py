"""App URLs"""

# Django
from django.urls import path, re_path

# AA Example
from example import views
from example.api import api

app_name: str = "example"  # pylint: disable=invalid-name

urlpatterns = [
    path("", views.index, name="index"),
    path("admin/", views.admin, name="admin"),
    # -- API System
    re_path(r"^api/", api.urls),
]
