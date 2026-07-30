"""PvE Views"""

# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# AA Belt Radar
from beltradar import __title__, forms
from beltradar.api.helpers.icons import (
    get_add_belt_timer_button,
    get_add_survey_button,
    get_survey_delete_button,
)
from beltradar.models import BeltSurveySession, BeltTimer
from beltradar.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


@login_required
@permission_required("beltradar.basic_access")
def index(request):
    """Index View"""
    context = {
        "title": "Index",
    }
    return render(request, "beltradar/view-index.html", context=context)


@login_required
@permission_required("beltradar.basic_access")
def create_session(request):
    context = {
        "title": "Create Belt Survey Session",
        "forms": {
            "create_session": forms.BeltSurveySessionForm(),
        },
    }
    if request.method == "POST":
        form = forms.BeltSurveySessionForm(request.POST)
        if form.is_valid():
            sess = form.save(commit=False)
            sess.owner = request.user
            sess.public_id = BeltSurveySession.generate_unique_public_id()
            sess.save()
            return redirect("beltradar:view_session", public_id=sess.public_id)
        context["forms"]["create_session"] = form  # return bound form with errors
    return render(request, "beltradar/view-create-session.html", context=context)


@login_required
@permission_required("beltradar.basic_access")
def create_timer(request, public_id):
    session = get_object_or_404(BeltSurveySession, public_id=public_id)
    context = {
        "title": "Create Belt Timer",
        "session": session,
        "forms": {
            "create_belt_timer": forms.BeltTimerForm(),
        },
    }
    if request.method == "POST":
        form = forms.BeltTimerForm(request.POST)
        if form.is_valid():
            timer: BeltTimer = form.save()
            timer.session.set([session])
            return redirect("beltradar:view_belt_timer", public_id=session.public_id)
        context["forms"]["create_timer"] = form  # return bound form with errors
    return render(request, "beltradar/view-create-timer.html", context=context)


@login_required
@permission_required("beltradar.basic_access")
def view_belt_timer(request, public_id):
    """View all survey sessions visible to the user."""
    session = get_object_or_404(BeltSurveySession, public_id=public_id)
    context = {
        "title": "View Belt Timer",
        "session": session,
        "forms": {
            "delete_belt_timer": forms.DeleteBeltTimerForm(),
        },
    }
    return render(request, "beltradar/view-user-belt-timer.html", context=context)


@login_required
@permission_required("beltradar.basic_access")
def view_session(request, public_id):
    session = get_object_or_404(BeltSurveySession, public_id=public_id)
    context = {
        "title": f"View Session - {session.name or session.public_id}",
        "session": session,
        "forms": {
            "delete_belt_timer": forms.DeleteBeltTimerForm(),
            "delete_snapshot": forms.DeleteSnapshotForm(),
            "delete_survey": forms.DeleteSurveyForm(),
            "add_survey": forms.AddSurveyForm(),
            "add_belt_timer": forms.BeltTimerForm(),
        },
        "delete_button": get_survey_delete_button(request=request, public_id=public_id),
        "add_survey_button": get_add_survey_button(
            request=request, public_id=public_id
        ),
        "add_belt_timer_button": get_add_belt_timer_button(
            request=request, public_id=public_id
        ),
    }
    return render(request, "beltradar/view-session.html", context=context)


@login_required
@permission_required("beltradar.basic_access")
def view_user_sessions(request):
    """View all survey sessions visible to the user."""
    context = {
        "title": "Survey Sessions Overview",
        "forms": {
            "delete_survey": forms.DeleteSurveyForm(),
        },
    }
    return render(request, "beltradar/view-user-sessions.html", context=context)


@login_required
@permission_required("beltradar.basic_access")
def view_my_sessions(request, character_id=None):
    if character_id is None:
        character_id = request.user.profile.main_character.character_id

    sessions = BeltSurveySession.objects.filter(owner=request.user).order_by(
        "-created_at"
    )
    context = {
        "title": "My Sessions",
        "character_id": character_id,
        "sessions": sessions,
        "forms": {
            "delete_survey": forms.DeleteSurveyForm(),
        },
    }
    return render(request, "beltradar/view-my-sessions.html", context=context)
