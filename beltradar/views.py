"""PvE Views"""

# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect, render
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# AA Belt Radar
from beltradar import __title__, tasks
from beltradar.models import Owner
from beltradar.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


@login_required
@permission_required("beltradar.basic_access")
def index(request):
    """Index View"""
    context = {
        "title": "Belt Radar",
    }
    return render(request, "beltradar/view-index.html", context=context)