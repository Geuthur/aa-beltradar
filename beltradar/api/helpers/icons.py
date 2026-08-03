# Django
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.authentication.decorators import permissions_required
from allianceauth.services.hooks import get_extension_logger

# AA Belt Radar
from beltradar import __title__
from beltradar.api.helpers.core import get_belt_timer_or_none, get_public_id_or_none
from beltradar.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


@permissions_required(
    [
        "beltradar.basic_access",
    ]
)
def get_survey_manage_action_icons(
    request: WSGIRequest,  # pylint: disable=unused-argument
    public_id: str,
) -> str | HttpResponse:
    """
    Generate HTML Action Icons for the My Sessions view.

    This function creates a set of action icons for managing survey sessions.
    The Buttons include Edit, Delete, and View, each represented by an icon depending on User's permissions.

    Args:
        request (WSGIRequest): The HTTP request object containing user information.
    Returns:
        SafeString: HTML string containing the action icons.
    """
    beltradar_request_icons = "<div class='d-flex justify-content-end'>"
    beltradar_request_icons += get_survey_view_button(
        request=request, public_id=public_id
    )
    beltradar_request_icons += get_survey_delete_button(
        request=request, public_id=public_id
    )
    beltradar_request_icons += "</div>"
    return beltradar_request_icons


@permissions_required(
    [
        "beltradar.basic_access",
    ]
)
def get_belt_timer_manage_action_icons(
    request: WSGIRequest,  # pylint: disable=unused-argument
    timer_id: int,
    character_id: int,
) -> str | HttpResponse:
    """
    Generate HTML Action Icons for the My Sessions view.

    This function creates a set of action icons for managing survey sessions.
    The Buttons include Edit, Delete, and View, each represented by an icon depending on User's permissions.

    Args:
        request (WSGIRequest): The HTTP request object containing user information.
    Returns:
        SafeString: HTML string containing the action icons.
    """
    beltradar_request_icons = "<div class='d-flex justify-content-end'>"
    beltradar_request_icons += get_timer_delete_button(
        request=request, timer_id=timer_id, character_id=character_id
    )
    beltradar_request_icons += "</div>"
    return beltradar_request_icons


def get_snapshot_delete_button(
    request: WSGIRequest,  # pylint: disable=unused-argument
    public_id: str,
    snapshot: str,
) -> str:
    """
    Generate a delete button for a specific snapshot in a survey session.

    This function creates an HTML button for deleting a snapshot within a survey session.
    When clicked, it triggers a modal to confirm the deletion of the snapshot.

    Args:
        public_id (str): The public UUID of the survey session.
        snapshot (str): The hash of the snapshot to delete.
    Returns:
        String: HTML string containing the delete button.
    """
    perms = get_public_id_or_none(request=request, public_id=public_id)[0]
    if not perms:
        return (
            ""  # Return an empty string if the user does not have permission to delete
        )

    # Generate the URL for the delete request
    button_request_delete_url = reverse(
        "beltradar:api:delete_snapshot",
        kwargs={
            "public_id": public_id,
            "snapshot": snapshot,
        },
    )

    # Define the icon and tooltip for the delete button
    icon = '<i class="fa-solid fa-trash"></i>'
    title = _("Delete Snapshot")
    color = "danger"

    # Create the HTML for the delete icon button
    delete_button = (
        f'<button data-action="{button_request_delete_url}" '
        f'class="btn btn-{color} btn-sm btn-square me-2" '
        'data-bs-toggle="modal" '
        'data-bs-tooltip="aa-beltradar" '
        'data-bs-target="#beltradar-accept-delete-snapshot" '
        f'data-snapshot="{snapshot}" '
        f'title="{title}">{icon}</button>'
    )
    return delete_button


def get_survey_delete_button(
    request: WSGIRequest, public_id: str  # pylint: disable=unused-argument
) -> str:
    """
    Generate a delete button for a specific survey session.

    This function creates an HTML button for deleting a survey session.
    When clicked, it triggers a modal to confirm the deletion of the survey session.

    Args:
        public_id (str): The public UUID of the survey session.
    Returns:
        String: HTML string containing the delete button.
    """

    perms = get_public_id_or_none(request=request, public_id=public_id)[0]
    if not perms:
        logger.debug(
            f"User {request.user} does not have permission to delete survey session {public_id}"
        )
        return (
            ""  # Return an empty string if the user does not have permission to delete
        )

    # Generate the URL for the delete request
    button_request_delete_url = reverse(
        "beltradar:api:delete_survey_session",
        kwargs={
            "public_id": public_id,
        },
    )

    # Define the icon and tooltip for the delete button
    icon = '<i class="fa-solid fa-trash"></i>'
    title = _("Delete Survey Session")
    color = "danger"

    # Create the HTML for the delete icon button
    delete_button = (
        f'<button data-action="{button_request_delete_url}" '
        f'class="btn btn-{color} btn-sm btn-square me-2" '
        'data-bs-toggle="modal" '
        'data-bs-tooltip="aa-beltradar" '
        'data-bs-target="#beltradar-accept-delete-survey-session" '
        f'title="{title}">{icon}</button>'
    )
    return delete_button


def get_add_survey_button(
    request: WSGIRequest, public_id: str  # pylint: disable=unused-argument
) -> str:
    """
    Generate an add button for a specific survey session.

    This function creates an HTML button for adding a new survey session.
    When clicked, it triggers a modal to display the add survey form.

    Args:
        public_id (str): The public UUID of the survey session.
    Returns:
        String: HTML string containing the add button.
    """

    # Generate the URL for the add request
    button_request_add_url = reverse(
        "beltradar:api:add_survey_entry",
        kwargs={
            "public_id": public_id,
        },
    )

    # Define the icon and tooltip for the add button
    icon = '<i class="fa-solid fa-plus"></i>'
    title = _("Add Survey")
    color = "success"

    # Create the HTML for the add icon button
    add_button = (
        f'<button data-action="{button_request_add_url}" '
        f'class="btn btn-{color} btn-sm btn-square me-2" '
        'data-bs-toggle="modal" '
        'data-bs-tooltip="aa-beltradar" '
        'data-bs-target="#beltradar-add-survey" '
        f'title="{title}">{icon}</button>'
    )
    return add_button


def get_survey_view_button(
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

    # Generate the URL for the view request
    button_request_view_url = reverse(
        "beltradar:view_session",
        kwargs={
            "public_id": public_id,
        },
    )

    # Define the icon and tooltip for the view button
    icon = '<i class="fa-solid fa-eye"></i>'
    title = _("View Survey Session")
    color = "primary"

    # Create the HTML for the view icon button
    view_button = (
        f'<a href="{button_request_view_url}" '
        f'class="btn btn-{color} btn-sm btn-square me-2" '
        'data-bs-tooltip="aa-beltradar" '
        f'title="{title}">{icon}'
        f"</a>"
    )
    return view_button


def get_add_belt_timer_button(
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

    # Generate the URL for the add request
    button_request_add_url = reverse(
        "beltradar:api:add_belt_timer",
    )

    # Define the icon and tooltip for the add button
    icon = '<i class="fa-solid fa-plus"></i>'
    title = _("Add Belt Timer")
    color = "success"

    # Create the HTML for the add icon button
    add_button = (
        f'<button data-action="{button_request_add_url}" '
        f'class="btn btn-{color} btn-sm btn-square me-2" '
        'data-bs-toggle="modal" '
        'data-bs-tooltip="aa-beltradar" '
        'data-bs-target="#beltradar-add-belt-timer" '
        f'title="{title}">{icon}</button>'
    )
    return add_button


def get_timer_delete_button(
    request: WSGIRequest,
    timer_id: int,  # pylint: disable=unused-argument
    character_id: int,  # pylint: disable=unused-argument
) -> str:
    """
    Generate a delete button for a specific belt timer.

    This function creates an HTML button for deleting a belt timer.
    When clicked, it triggers a modal to confirm the deletion of the belt timer.

    Args:
        timer_id (int): The ID of the belt timer.
    Returns:
        String: HTML string containing the delete button.
    """

    perms = get_belt_timer_or_none(request=request, character_id=character_id)[0]
    if not perms:
        return (
            ""  # Return an empty string if the user does not have permission to delete
        )

    # Generate the URL for the delete request
    button_request_delete_url = reverse(
        "beltradar:api:delete_belt_timer",
        kwargs={
            "timer_id": timer_id,
        },
    )

    # Define the icon and tooltip for the delete button
    icon = '<i class="fa-solid fa-trash"></i>'
    title = _("Delete Belt Timer")
    color = "danger"

    # Create the HTML for the delete icon button
    delete_button = (
        f'<button data-action="{button_request_delete_url}" '
        f'class="btn btn-{color} btn-sm btn-square me-2" '
        'data-bs-toggle="modal" '
        'data-bs-tooltip="aa-beltradar" '
        'data-bs-target="#beltradar-accept-delete-belt-timer" '
        f'title="{title}">{icon}</button>'
    )
    return delete_button
