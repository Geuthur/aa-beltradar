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

# AA Example
from example import __title__, tasks
from example.models import Example
from example.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


@login_required
@permission_required("example.basic_access")
def index(request):
    """Index View"""
    context = {
        "title": "Example",
    }
    return render(request, "example/view-index.html", context=context)


@login_required
@permission_required("example.basic_access")
def admin(request: WSGIRequest):
    # Check Permissions
    if not request.user.is_superuser:
        messages.error(request, _("You do not have permission to access this page."))
        return redirect("example:index")

    # Handle Character
    def _handle_character_updates(force_refresh):
        character_id = request.POST.get("character_id")
        if character_id:
            try:
                character = Example.objects.get(
                    eve_character__character_id=int(character_id)
                )
                msg = format_lazy(
                    _("Queued Update for Character: {character_name}"),
                    character_name=character.eve_character.character_name,
                )
                messages.info(request, msg)
                tasks.update_example.apply_async(
                    kwargs={
                        "eve_id": character.eve_character.character_id,
                        "force_refresh": force_refresh,
                    },
                    priority=7,
                )
            except (ValueError, Example.DoesNotExist):
                msg = format_lazy(
                    _("Character with ID {character_id} not found"),
                    character_id=character_id,
                )
                messages.error(request, msg)
            return
        messages.info(request, _("Queued Update All Characters"))
        return

    # Handle POST Requests
    if request.method == "POST":
        force_refresh = bool(request.POST.get("force_refresh", False))

        # General Tasks
        if request.POST.get("run_example"):
            messages.info(request, _("Queued Example Task"))
            tasks.example_task.apply_async(priority=1)
        # Specific Tasks
        if request.POST.get("run_character_updates"):
            _handle_character_updates(force_refresh)
    return render(request, "example/view-administration.html")
