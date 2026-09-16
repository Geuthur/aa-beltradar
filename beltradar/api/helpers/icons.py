# Standard Library
from typing import TYPE_CHECKING

# Django
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import ObjectDoesNotExist
from django.http import HttpResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.authentication.decorators import permissions_required
from allianceauth.services.hooks import get_extension_logger

# AA Belt Radar
from beltradar import __title__
from beltradar.api import schema
from beltradar.api.helpers.core import (
    get_manage_belt_timer_or_none,
    get_manage_session_or_none,
)
from beltradar.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


if TYPE_CHECKING:
    # AA Belt Radar
    from beltradar.models.beltradar import BeltSurveySession, BeltTimer


@permissions_required(
    [
        "beltradar.basic_access",
    ]
)
def session_manage_action_icons(
    request: WSGIRequest,  # pylint: disable=unused-argument
    session: "BeltSurveySession",
) -> str | HttpResponse:
    """
    Generate HTML Action Icons for the Session Overview view.

    This function creates a set of action icons for managing sessions.
    The buttons include Edit, Delete, and View, each represented by an icon depending on User's permissions.

    Args:
        request (WSGIRequest): The HTTP request object containing user information.
        session (BeltSurveySession): The session object for which to generate action icons.
    Returns:
        ActionSchema | None: The action icons schema for the session, or None if the session does not exist.
    """
    perms, session = get_manage_session_or_none(
        request=request, public_id=session.public_id
    )

    # Return an empty string if the session does not exist
    if session is None:
        return None

    beltradar_request_icons = None

    if perms:
        beltradar_request_icons = schema.ActionSchema(
            delete=schema.ModalSchema(
                url=reverse(
                    "beltradar:api:delete_session",
                    kwargs={"public_id": session.public_id},
                ),
                icon="fa-solid fa-trash",
                title=str(_("Delete Session")),
                text=str(_("Are you sure you want to delete this session?")),
                color="danger",
                modal_id="beltradar-accept-delete-session",
            ),
            update=schema.ModalSchema(
                url=reverse(
                    "beltradar:api:modify_session",
                    kwargs={
                        "public_id": session.public_id,
                        "field": "is_public",
                        "value": str(not session.is_public).capitalize(),
                    },
                ),
                icon="fa-solid fa-wrench",
                title=str(_("Modify Session")),
                text=str(
                    _(
                        "Are you sure you want to switch public/private status for this session?"
                    )
                ),
                color="warning",
                modal_id="beltradar-accept-modify-session",
            ),
        )
    return beltradar_request_icons


@permissions_required(
    [
        "beltradar.basic_access",
    ]
)
def session_belt_timer_action_icons(
    request: WSGIRequest,  # pylint: disable=unused-argument
    public_id: str,
) -> str | HttpResponse:
    """
    Generate HTML Action Icons for the Session view.

    This function creates a set of action icons for managing belt timers.
    The buttons include Edit, Delete, and View, each represented by an icon depending on User's permissions.

    Args:
        request (WSGIRequest): The HTTP request object containing user information.
    Returns:
        SafeString: HTML string containing the action icons.
    """
    perms, session = get_manage_session_or_none(request=request, public_id=public_id)
    if not perms:
        return None  # Return None if the user does not have permission

    if session.is_timer_ready:
        if not session.has_timer:
            return schema.ActionSchema(
                create=schema.ModalSchema(
                    url=reverse(
                        "beltradar:api:add_session_belt_timer",
                        kwargs={"public_id": public_id},
                    ),
                    icon="fa-solid fa-plus",
                    title=str(_("Create Belt Timer")),
                    text=str(
                        _(
                            "Are you sure you want to create a belt timer for this session?"
                        )
                    ),
                    color="success",
                    modal_id="beltradar-accept-create-belt-timer",
                )
            )
        try:
            timer = session.br_belt_timer
            return schema.ActionSchema(
                delete=schema.ModalSchema(
                    url=reverse(
                        "beltradar:api:delete_belt_timer", kwargs={"timer_id": timer.pk}
                    ),
                    icon="fa-solid fa-trash",
                    title=str(_("Delete Belt Timer")),
                    text=str(_("Are you sure you want to delete this belt timer?")),
                    color="danger",
                    modal_id="beltradar-accept-delete-belt-timer",
                )
            )
        except ObjectDoesNotExist:
            pass
    return None  # Return None if no action icons are applicable


@permissions_required(
    [
        "beltradar.basic_access",
    ]
)
def belt_timer_manage_action_icons(
    request: WSGIRequest,  # pylint: disable=unused-argument
    timer: "BeltTimer",  # pylint: disable=unused-argument
) -> str | HttpResponse:
    """
    Generate HTML Action Icons for the Belt Timer view.

    This function creates a set of action icons for managing belt timers.
    The buttons include Edit, Delete, and View, each represented by an icon depending on User's permissions.

    Args:
        request (WSGIRequest): The HTTP request object containing user information.
    Returns:
        SafeString: HTML string containing the action icons.
    """
    perms = get_manage_belt_timer_or_none(request=request, timer_pk=timer.pk)[0]
    if not perms:
        return None  # Return None if the user does not have permission to manage the belt timer

    actions_schema = schema.ActionSchema()
    # Modify button for the belt timer
    title = _("Modify Belt Timer")
    actions_schema.update = schema.ModalSchema(
        url=reverse(
            "beltradar:api:modify_belt_timer",
            kwargs={
                "timer_id": timer.pk,
                "field": "is_public",
                "value": str(not timer.is_public).capitalize(),
            },
        ),
        icon="fa-solid fa-wrench",
        text=str(_("Are you sure you want to modify this belt timer?")),
        title=str(title),
        color="warning",
        modal_id="beltradar-accept-modify-belt-timer",
    )
    # Delete button for the belt timer
    title = _("Delete Belt Timer")
    actions_schema.delete = schema.ModalSchema(
        url=reverse("beltradar:api:delete_belt_timer", kwargs={"timer_id": timer.pk}),
        icon="fa-solid fa-trash",
        text=str(_("Are you sure you want to delete this belt timer?")),
        title=str(title),
        color="danger",
        modal_id="beltradar-accept-delete-belt-timer",
    )
    return actions_schema


def get_snapshot_add_button(
    request: WSGIRequest, public_id: str  # pylint: disable=unused-argument
) -> str:
    """
    Generate an add button for a specific snapshot.

    This function creates an HTML button for adding a new snapshot.
    When clicked, it triggers a modal to display the add snapshot form.

    Args:
        public_id (str): The public UUID of the snapshot's session.
    Returns:
        String: HTML string containing the add button.
    """
    # Create the HTML for the add icon button
    title = _("Add Snapshot")
    add_button = schema.ModalSchema(
        url=reverse("beltradar:api:add_snapshot", kwargs={"public_id": public_id}),
        icon="fa-solid fa-plus",
        text=str(_("Add Snapshot")),
        title=str(title),
        color="success",
        modal_id="beltradar-add-snapshot",
    )
    return add_button


def get_snapshot_delete_button(
    request: WSGIRequest,  # pylint: disable=unused-argument
    public_id: str,
    identifier: str = None,  # pylint: disable=unused-argument
) -> str:
    """
    Generate a delete button for a specific snapshot in a session.

    This function creates an HTML button for deleting a snapshot within a session.
    When clicked, it triggers a modal to confirm the deletion of the snapshot.

    Args:
        public_id (str): The public UUID of the session.
        identifier (str): The snapshot identifier to be deleted. If not provided, the last snapshot will be used.
    Returns:
        String: HTML string containing the delete button.
    """
    perms, session = get_manage_session_or_none(request=request, public_id=public_id)
    if not perms:
        return None  # Return None if the user does not have permission to delete

    # If snapshot is not provided, get the last snapshot from the session
    if identifier is None:
        try:
            identifier = (
                session.br_snapshots.last().identifier
            )  # Get the last snapshot if not provided
        except AttributeError:
            return None  # Return None if there are no snapshots available

    # Create the HTML for the delete icon button
    title = _("Delete Snapshot")
    delete_button = schema.ModalSchema(
        url=reverse(
            "beltradar:api:delete_snapshot",
            kwargs={"public_id": public_id, "identifier": identifier},
        ),
        icon="fa-solid fa-trash",
        text=str(_("Are you sure you want to delete this snapshot?")),
        title=str(title),
        color="danger",
        modal_id="beltradar-accept-delete-snapshot",
    )
    return delete_button


def get_session_add_button(
    request: WSGIRequest,  # pylint: disable=unused-argument
) -> str:
    """
    Generate an add button for a specific session.

    This function creates an HTML button for adding a new session.
    When clicked, it triggers a modal to display the add session form.

    Args:
        request (WSGIRequest): The HTTP request object.
    Returns:
        String: HTML string containing the add button.
    """
    # Create the HTML for the add icon button
    title = _("Add Session")
    add_button = schema.ModalSchema(
        url=reverse("beltradar:api:add_session"),
        icon="fa-solid fa-plus",
        text=str(title),
        title=str(title),
        color="success",
        modal_id="beltradar-add-session",
    )
    return add_button


def get_session_delete_button(
    request: WSGIRequest, public_id: str  # pylint: disable=unused-argument
) -> str:
    """
    Generate a delete button for a specific session.

    This function creates an HTML button for deleting a session.
    When clicked, it triggers a modal to confirm the deletion of the session.

    Args:
        public_id (str): The public UUID of the session.
    Returns:
        String: HTML string containing the delete button.
    """
    perms = get_manage_session_or_none(request=request, public_id=public_id)[0]
    if not perms:
        return (
            ""  # Return an empty string if the user does not have permission to delete
        )

    # Create the HTML for the delete icon button
    title = _("Delete Session")
    delete_button = schema.ModalSchema(
        url=reverse("beltradar:api:delete_session", kwargs={"public_id": public_id}),
        icon="fa-solid fa-trash",
        text=str(title),
        title=str(title),
        color="danger",
        modal_id="beltradar-accept-delete-session",
    )
    return delete_button


def get_session_view_button(
    request: WSGIRequest, public_id: str  # pylint: disable=unused-argument
) -> str:
    """
    Generate a view button for a specific survey session.

    This function creates an HTML button for viewing a survey session.
    When clicked, it triggers a modal to display the survey session details.

    Args:
        public_id (str): The public UUID of the survey session.
    Returns:
        String: HTML string containing the view button.
    """
    title = _("View Session")
    # Create the HTML for the view icon button
    view_button = schema.ModalSchema(
        url=reverse("beltradar:view_session", kwargs={"public_id": public_id}),
        icon="fa-solid fa-eye",
        text=str(title),
        title=str(title),
        color="primary",
    )
    return view_button


def get_session_status_icon(
    session: "BeltSurveySession",
) -> str:
    """
    Generate a status icon for a specific belt session.

    This function creates an HTML icon indicating whether a belt session is public or private.

    Args:
        session (BeltSurveySession): The belt session object.
    Returns:
        String: HTML string containing the status icon.
    """
    # Define the icon and tooltip based on the public status of the belt timer
    if session.is_public:
        icon = '<i class="fa-solid fa-globe"></i>'
        title = _("Public Belt Session")
        color = "success"
    else:
        icon = '<i class="fa-solid fa-lock"></i>'
        title = _("Private Belt Session")
        color = "secondary"

    # Create the HTML for the public/private icon
    public_icon = f"<button type='button' data-bs-tooltip='aa-beltradar' class='btn btn-{color}' title='{title}'>{icon}</button>"
    return public_icon


def get_belt_timer_add_button(
    request: WSGIRequest,  # pylint: disable=unused-argument
) -> str:
    """
    Generate an add button for a specific belt timer.

    This function creates an HTML button for adding a new belt timer.
    When clicked, it triggers a modal to display the add belt timer form.

    Args:
        request (WSGIRequest): The HTTP request object.
    Returns:
        String: HTML string containing the add button.
    """
    title = _("Add Belt Timer")
    add_button = schema.ModalSchema(
        url="beltradar:api:add_belt_timer",
        icon="fa-solid fa-plus",
        text=title,
        title=title,
        color="success",
        modal_id="beltradar-add-belt-timer",
    )
    return add_button


def get_belt_timer_status_icon(
    timer: "BeltTimer",
) -> str:
    """
    Generate a status icon for a specific belt timer.

    This function creates an HTML icon indicating whether a belt timer is public or private.

    Args:
        timer (BeltTimer): The belt timer object.
    Returns:
        String: HTML string containing the status icon.
    """
    # Define the icon and tooltip based on the public status of the belt timer
    if timer.is_public:
        icon = '<i class="fa-solid fa-globe"></i>'
        title = _("Public Belt Timer")
        color = "success"
    else:
        icon = '<i class="fa-solid fa-lock"></i>'
        title = _("Private Belt Timer")
        color = "secondary"

    # Create the HTML for the public/private icon
    public_icon = f"<button type='button' data-bs-tooltip='aa-beltradar' class='btn btn-{color}' title='{title}'>{icon}</button>"
    return public_icon
