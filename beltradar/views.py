"""PvE Views"""

# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from eve_sde.models import ItemType

# AA Belt Radar
from beltradar import __title__, forms
from beltradar.api import schema
from beltradar.api.helpers.icons import get_survey_delete_button
from beltradar.models import BeltSurveyEntry, BeltSurveySession
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
        logger.debug(f"Create session form data: {request.POST}")
        if form.is_valid():
            sess = form.save(commit=False)
            sess.owner = request.user
            sess.save()
            return redirect("beltradar:view_session", public_id=sess.public_id)
        context["forms"]["create_session"] = form  # return bound form with errors
    logger.debug(f"Rendering create session form with context: {context}")
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
        },
        "stats": session.mining_stats(),
        "delete_button": get_survey_delete_button(request=request, public_id=public_id),
    }
    return render(request, "beltradar/view-session.html", context=context)


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


@login_required
@permission_required("beltradar.basic_access")
def add_entry(request, public_id):
    session = get_object_or_404(BeltSurveySession, public_id=public_id)
    context = {
        "title": f"Survey - {session.name or session.public_id}",
        "session": session,
        "forms": {
            "ore_batch_import": forms.OreBatchImportForm(),
        },
        "error_message": None,
    }
    # If this is a POST request, we need to process the form data.
    if request.method == "POST":
        form = forms.OreBatchImportForm(request.POST)
        entries = []
        if session.is_fresh:
            context["error_message"] = _(
                "This session has been recently updated. Please wait a few minutes before adding new entries."
            )
            context["forms"][
                "ore_batch_import"
            ] = form  # return bound form so template can render errors
            return render(request, "beltradar/view-add-survey.html", context=context)

        if form.is_valid():
            data: list[schema.OreSchema] = getattr(
                form, "parsed_items", form.cleaned_data.get("parsed_items", [])
            )
            missing_types = []
            names = [item.name for item in data]
            eve_items = ItemType.objects.filter(name__in=names)
            existing_type_names = set(eve_items.values_list("name", flat=True))
            eve_map = {e.name: e for e in eve_items}

            for item in data:
                if item.name not in existing_type_names:
                    missing_types.append(item.name)
                    continue  # skip items with missing types

                eve_type = eve_map[item.name]
                entry = BeltSurveyEntry(
                    session=session,
                    recorded_by=request.user,
                    eve_type=eve_type,
                    units=item.units,
                    volume_left=item.volume_m3,
                    price=float(item.price_isk),
                    note=(
                        f"Added via batch import. Missing types: {', '.join(missing_types)}"
                        if missing_types
                        else "Added via batch import."
                    ),
                    snapshot=item.snapshot,
                )
                entries.append(entry)
            if entries:
                with transaction.atomic():
                    BeltSurveyEntry.objects.bulk_create(entries)
            return redirect("beltradar:view_session", public_id=public_id)
        context["error_message"] = _(
            "Failed to parse the raw data. Please check the format and try again."
        )
        # return the bound form so template can render errors
        context["forms"]["ore_batch_import"] = form
    return render(request, "beltradar/view-add-survey.html", context=context)
