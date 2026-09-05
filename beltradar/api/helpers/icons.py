# Standard Library
from typing import TYPE_CHECKING

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
from beltradar.api.helpers.core import (
    get_manage_belt_timer_or_none,
    get_manage_session_or_none,
)
from beltradar.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


if TYPE_CHECKING:
    # AA Belt Radar
    from beltradar.models.beltradar import BeltSurveySession, BeltTimer


def _create_button(
    url_name: str,
    url_kwargs: dict,
    text: str,
    title: str,
    color: str,
    modal_id: str = None,
) -> str:
    """
    Helper function to create an HTML button with the specified parameters.

    Args:
        request (WSGIRequest): The HTTP request object.
        url_name (str): The name of the URL pattern to reverse.
        url_kwargs (dict): The keyword arguments for the URL reversal.
        text (str): The HTML for the text or icon to display on the button.
        title (str): The tooltip text for the button.
        color (str): The Bootstrap color class for the button.
        modal_id (str): The ID of the modal to trigger on click.

    Returns:
        str: HTML string containing the button.
    """
    # Generate the URL for the action
    button_url = reverse(url_name, kwargs=url_kwargs)

    # Create the HTML for the button
    button_html = "<"
    if modal_id:
        button_html += f'button data-action="{button_url}" data-bs-toggle="modal" data-bs-target="#{modal_id}" '
    else:
        button_html += f'a href="{button_url}" '
    button_html += f'class="btn btn-{color} btn-sm btn-square me-2" '
    button_html += f'data-bs-tooltip="aa-beltradar" title="{title}">{text}'
    if modal_id:
        button_html += "</button>"
    else:
        button_html += "</a>"
    return button_html


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
    Returns:
        SafeString: HTML string containing the action icons.
    """
    perms, session = get_manage_session_or_none(
        request=request, public_id=session.public_id
    )

    beltradar_request_icons = "<div class='d-flex justify-content-end'>"
    # Add the view session button
    beltradar_request_icons += get_session_view_button(
        request=request, public_id=session.public_id
    )

    # Check if the user has permissions to modify or delete the session
    if perms:
        # Add the modify session button (toggle public/private)
        beltradar_request_icons += _create_button(
            url_name="beltradar:api:modify_session",
            url_kwargs={
                "public_id": session.public_id,
                "field": "is_public",
                "value": str(not session.is_public).capitalize(),
            },
            text='<i class="fa-solid fa-wrench"></i>',
            title=_("Modify Session"),
            color="warning",
            modal_id="beltradar-accept-modify-session",
        )
        # Add the delete session button
        beltradar_request_icons += _create_button(
            url_name="beltradar:api:delete_session",
            url_kwargs={"public_id": session.public_id},
            text='<i class="fa-solid fa-trash"></i>',
            title=_("Delete Session"),
            color="danger",
            modal_id="beltradar-accept-delete-session",
        )

    beltradar_request_icons += "</div>"

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
        return ""  # Return empty string if the user does not have permission

    if session.is_timer_ready:
        text = _("Create Belt Timer")
        return _create_button(
            url_name="beltradar:api:add_session_belt_timer",
            url_kwargs={"public_id": public_id},
            text=text,
            title=text,
            color="success",
            modal_id="beltradar-accept-create-belt-timer",
        )
    if session.br_belt_timer.exists():
        timer_id = session.br_belt_timer.get(public_id=public_id).pk
        text = _("Delete Belt Timer")
        return _create_button(
            url_name="beltradar:api:delete_belt_timer",
            url_kwargs={"timer_id": timer_id},
            text=text,
            title=text,
            color="danger",
            modal_id="beltradar-accept-delete-belt-timer",
        )
    return ""


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
        return (
            ""  # Return an empty string if the user does not have permission to delete
        )

    beltradar_request_icons = "<div class='d-flex justify-content-end'>"
    # Modify button for the belt timer
    beltradar_request_icons += _create_button(
        url_name="beltradar:api:modify_belt_timer",
        url_kwargs={
            "timer_id": timer.pk,
            "field": "is_public",
            "value": str(not timer.is_public).capitalize(),
        },
        text='<i class="fa-solid fa-wrench"></i>',
        title=_("Edit Belt Timer"),
        color="warning",
        modal_id="beltradar-accept-modify-belt-timer",
    )
    # Delete button for the belt timer
    beltradar_request_icons += _create_button(
        url_name="beltradar:api:delete_belt_timer",
        url_kwargs={"timer_id": timer.pk},
        text='<i class="fa-solid fa-trash"></i>',
        title=_("Delete Belt Timer"),
        color="danger",
        modal_id="beltradar-accept-delete-belt-timer",
    )
    beltradar_request_icons += "</div>"
    return beltradar_request_icons


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
    add_button = _create_button(
        url_name="beltradar:api:add_snapshot",
        url_kwargs={"public_id": public_id},
        text='<i class="fa-solid fa-plus"></i>',
        title=_("Add Snapshot"),
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
        return (
            ""  # Return an empty string if the user does not have permission to delete
        )

    # If snapshot is not provided, get the last snapshot from the session
    if identifier is None:
        try:
            identifier = (
                session.br_snapshots.last().identifier
            )  # Get the last snapshot if not provided
        except AttributeError:
            return ""  # Return an empty string if there are no snapshots available

    # Create the HTML for the delete icon button
    delete_button = _create_button(
        url_name="beltradar:api:delete_snapshot",
        url_kwargs={"public_id": public_id, "identifier": identifier},
        text='<i class="fa-solid fa-trash"></i>',
        title=_("Delete Snapshot"),
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
    add_button = _create_button(
        url_name="beltradar:api:add_session",
        url_kwargs={},
        text='<i class="fa-solid fa-plus"></i>',
        title=_("Add Session"),
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
    delete_button = _create_button(
        url_name="beltradar:api:delete_session",
        url_kwargs={"public_id": public_id},
        text='<i class="fa-solid fa-trash"></i>',
        title=_("Delete Session"),
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
    # Create the HTML for the view icon button
    view_button = _create_button(
        url_name="beltradar:view_session",
        url_kwargs={"public_id": public_id},
        text='<i class="fa-solid fa-eye"></i>',
        title=_("View Session"),
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
    # Create the HTML for the add icon button
    add_button = _create_button(
        url_name="beltradar:api:add_belt_timer",
        url_kwargs={},
        text='<i class="fa-solid fa-plus"></i>',
        title=_("Add Belt Timer"),
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
