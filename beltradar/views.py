"""PvE Views"""

# Django
from django.contrib import messages
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
from beltradar.models import BeltSurveySession, UserSettings
from beltradar.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


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
            sess.save()
            return redirect("beltradar:view_session", public_id=sess.public_id)
        context["forms"]["create_session"] = form  # return bound form with errors
    return render(request, "beltradar/view-create-session.html", context=context)


@login_required
@permission_required("beltradar.basic_access")
def view_session(request, public_id):
    session = get_object_or_404(BeltSurveySession, public_id=public_id)
    context = {
        "title": f"View Session - {session.name or session.public_id}",
        "session": session,
        "forms": {
            "delete_snapshot": forms.DeleteSnapshotForm(),
            "delete_survey": forms.DeleteSurveyForm(),
            "add_survey": forms.AddSurveyForm(),
        },
        "delete_button": get_survey_delete_button(request=request, public_id=public_id),
        "add_survey_button": get_add_survey_button(
            request=request, public_id=public_id
        ),
    }
    return render(request, "beltradar/view-session.html", context=context)


@login_required
@permission_required("beltradar.basic_access")
def view_belt_radar(request):
    """View all survey sessions visible to the user."""
    context = {
        "title": "Survey Sessions Overview",
        "forms": {
            "add_belt_timer": forms.BeltTimerForm(),
            "switch_belt_timer": forms.SwitchBeltTimerForm(),
            "delete_survey": forms.DeleteSurveyForm(),
            "delete_belt_timer": forms.DeleteBeltTimerForm(),
        },
        "add_belt_timer_button": get_add_belt_timer_button(request=request),
    }
    return render(request, "beltradar/view-belt-radar.html", context=context)


@login_required
@permission_required("beltradar.basic_access")
def view_my_beltradar(request, character_id=None):
    if character_id is None:
        character_id = request.user.profile.main_character.character_id

    context = {
        "title": "My Sessions",
        "character_id": character_id,
        "forms": {
            "add_belt_timer": forms.BeltTimerForm(),
            "switch_belt_timer": forms.SwitchBeltTimerForm(),
            "delete_survey": forms.DeleteSurveyForm(),
            "delete_belt_timer": forms.DeleteBeltTimerForm(),
        },
        "add_belt_timer_button": get_add_belt_timer_button(request=request),
    }
    return render(request, "beltradar/view-my-belt-radar.html", context=context)


@login_required
@permission_required("beltradar.basic_access")
def view_my_settings(request):
    """View user settings."""
    # Get or create user settings for the logged-in user
    user_settings = UserSettings.objects.get_or_create(user=request.user)[0]

    # Create a form instance with the user settings
    user_settings_form = forms.UserSettingsForm(instance=user_settings)

    if request.method == "POST":
        # Create a form instance with the POST data and the user settings instance
        user_settings_form = forms.UserSettingsForm(
            request.POST, instance=user_settings
        )

        # If the form is valid, save the user settings and display a success message
        if user_settings_form.is_valid():
            user_settings_form.save()

            # Display a success message
            messages.success(request=request, message=_("Settings saved."))

            # Redirect back to the user settings page
            return redirect("beltradar:view_my_settings")

    # Create a context dictionary with the title and the form instance
    context = {
        "title": "User Settings",
        "forms": {
            "settings": user_settings_form,
        },
    }

    return render(request, "beltradar/view-my-settings.html", context=context)


@login_required
@permission_required("beltradar.basic_access")
def create_belt_timer(request):
    """Create a new belt timer."""
    context = {
        "title": "Create Belt Timer",
        "forms": {
            "create_belt_timer": forms.BeltTimerForm(),
        },
    }
    if request.method == "POST":
        form = forms.BeltTimerForm(request.POST)
        if form.is_valid():
            timer = form.save(commit=False)
            timer.owner = request.user
            timer.save()
            return redirect("beltradar:view_my_beltradar")
        context["forms"]["create_belt_timer"] = form  # return bound form with errors
    return render(request, "beltradar/view-create-timer.html", context=context)
