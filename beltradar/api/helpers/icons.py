# Standard Library
from typing import TYPE_CHECKING

# Django
from django.core.exceptions import ObjectDoesNotExist
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


if TYPE_CHECKING:
    # AA Belt Radar
    from beltradar.models.beltradar import BeltTimer


def _create_button(
    url_name: str,
    url_kwargs: dict,
    icon: str,
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
        icon (str): The HTML for the icon to display on the button.
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
    button_html += f'data-bs-tooltip="aa-beltradar" title="{title}">{icon}'
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
def survey_manage_action_icons(
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


def survey_timer_button_icons(
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
    perms, session = get_public_id_or_none(request=request, public_id=public_id)
    if not perms:
        return "N/A"  # Return an empty string if the user does not have permission to delete

    if not session.br_belt_timer.exists():
        timer_button_icon = _create_button(
            url_name="beltradar:api:add_survey_timer",
            url_kwargs={"public_id": public_id},
            icon='<i class="fa-solid fa-plus"></i>',
            title=_("Create Belt Timer"),
            color="success",
            modal_id="beltradar-accept-create-survey-timer",
        )
    else:
        try:
            timer_id = session.br_belt_timer.get(public_id=public_id).pk
            timer_button_icon = _create_button(
                url_name="beltradar:api:delete_belt_timer",
                url_kwargs={"timer_id": timer_id},
                icon='<i class="fa-solid fa-trash"></i>',
                title=_("Delete Belt Timer"),
                color="danger",
                modal_id="beltradar-accept-delete-belt-timer",
            )
        except ObjectDoesNotExist:
            timer_button_icon = "N/A"
    return timer_button_icon


@permissions_required(
    [
        "beltradar.basic_access",
    ]
)
def belt_timer_manage_action_icons(
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

    # Create the HTML for the delete icon button
    delete_button = _create_button(
        url_name="beltradar:api:delete_snapshot",
        url_kwargs={"public_id": public_id, "snapshot": snapshot},
        icon='<i class="fa-solid fa-trash"></i>',
        title=_("Delete Snapshot"),
        color="danger",
        modal_id="beltradar-accept-delete-snapshot",
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

    # Create the HTML for the delete icon button
    delete_button = _create_button(
        url_name="beltradar:api:delete_survey_session",
        url_kwargs={"public_id": public_id},
        icon='<i class="fa-solid fa-trash"></i>',
        title=_("Delete Survey Session"),
        color="danger",
        modal_id="beltradar-accept-delete-survey-session",
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
    # Create the HTML for the add icon button
    add_button = _create_button(
        url_name="beltradar:api:add_survey_entry",
        url_kwargs={"public_id": public_id},
        icon='<i class="fa-solid fa-plus"></i>',
        title=_("Add Survey"),
        color="success",
        modal_id="beltradar-add-survey",
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
    # Create the HTML for the view icon button
    view_button = _create_button(
        url_name="beltradar:view_session",
        url_kwargs={"public_id": public_id},
        icon='<i class="fa-solid fa-eye"></i>',
        title=_("View Survey Session"),
        color="primary",
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
    # Create the HTML for the add icon button
    add_button = _create_button(
        url_name="beltradar:api:add_belt_timer",
        url_kwargs={},
        icon='<i class="fa-solid fa-plus"></i>',
        title=_("Add Belt Timer"),
        color="success",
        modal_id="beltradar-add-belt-timer",
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

    # Create the HTML for the delete icon button
    delete_button = _create_button(
        url_name="beltradar:api:delete_belt_timer",
        url_kwargs={"timer_id": timer_id},
        icon='<i class="fa-solid fa-trash"></i>',
        title=_("Delete Belt Timer"),
        color="danger",
        modal_id="beltradar-accept-delete-belt-timer",
    )
    return delete_button


def switch_belt_timer_state(
    timer: "BeltTimer",
) -> str:
    """
    Generate a switch state icon for a specific belt timer.

    This function creates an HTML icon indicating whether a belt timer is public or private.

    Args:
        timer (BeltTimer): The belt timer object.
    Returns:
        String: HTML string containing the switch state icon.
    """
    # Define the icon and tooltip based on the public status of the belt timer
    if timer.public:
        icon = '<i class="fa-solid fa-globe"></i>'
        title = _("Public Belt Timer")
        color = "success"
    else:
        icon = '<i class="fa-solid fa-lock"></i>'
        title = _("Private Belt Timer")
        color = "secondary"

    # Create the HTML for the public/private icon
    public_icon = _create_button(
        url_name="beltradar:api:modify_belt_timer",
        url_kwargs={
            "timer_id": timer.pk,
            "field": "public",
            "value": str(not timer.public).capitalize(),
        },
        icon=icon,
        title=title,
        color=color,
        modal_id="beltradar-accept-switch-belt-timer",
    )
    return public_icon
