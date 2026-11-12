# Standard Library
from typing import TYPE_CHECKING

# Django
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import ObjectDoesNotExist
from django.urls import reverse

# AA Belt Radar
from beltradar.api import schema
from beltradar.api.helpers.core import (
    get_manage_belt_timer_or_none,
    get_manage_session_or_none,
    get_session_or_none,
)
from beltradar.models import General

if TYPE_CHECKING:
    # AA Belt Radar
    from beltradar.models.beltradar import BeltSurveySession, BeltTimer


# The API only tells which actions the user may perform. Icon, title and texts live in the frontend.


def session_manage_actions(
    request: WSGIRequest,
    session: "BeltSurveySession",
) -> schema.ActionSchema | None:
    """
    Get the actions the user may perform on a session in the Session Overview.

    Args:
        request (WSGIRequest): The HTTP request object containing user information.
        session (BeltSurveySession): The session object for which to get the actions.
    Returns:
        ActionSchema | None: The actions for the session, or None if the user may not manage it.
    """
    if not General.objects.has_basic_access(request.user):
        return None

    perms, session = get_manage_session_or_none(
        request=request, public_id=session.public_id
    )

    if session is None or not perms:
        return None

    return schema.ActionSchema(
        delete=schema.ModalSchema(
            url=reverse(
                "beltradar:api:delete_session",
                kwargs={"public_id": session.public_id},
            ),
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
            modal_id="beltradar-accept-modify-session",
        ),
    )


def session_belt_timer_actions(
    request: WSGIRequest,
    public_id: str,
) -> schema.ActionSchema | None:
    """
    Get the belt timer actions the user may perform in the Session view.

    Args:
        request (WSGIRequest): The HTTP request object containing user information.
        public_id (str): The public ID of the session.
    Returns:
        ActionSchema | None: The belt timer actions, or None if none are applicable.
    """
    if not General.objects.has_basic_access(request.user):
        return None

    perms, session = get_manage_session_or_none(request=request, public_id=public_id)
    if not perms:
        return None

    if session.is_auto_timer_ready:
        if not session.has_timer:
            return schema.ActionSchema(
                create=schema.ModalSchema(
                    url=reverse(
                        "beltradar:api:add_session_belt_timer",
                        kwargs={"public_id": public_id},
                    ),
                    modal_id="beltradar-accept-create-belt-timer",
                )
            )
        try:
            timer = session.br_belt_timer
            return schema.ActionSchema(
                update=schema.ModalSchema(
                    url=reverse(
                        "beltradar:api:modify_belt_timer",
                        kwargs={"timer_id": timer.pk},
                    ),
                    modal_id="beltradar-accept-modify-belt-timer",
                ),
                delete=schema.ModalSchema(
                    url=reverse(
                        "beltradar:api:delete_belt_timer", kwargs={"timer_id": timer.pk}
                    ),
                    modal_id="beltradar-accept-delete-belt-timer",
                ),
            )
        except ObjectDoesNotExist:
            pass
    return None


def belt_timer_manage_actions(
    request: WSGIRequest,
    timer: "BeltTimer",
) -> schema.ActionSchema | None:
    """
    Get the actions the user may perform on a belt timer.

    Args:
        request (WSGIRequest): The HTTP request object containing user information.
        timer (BeltTimer): The belt timer.
    Returns:
        ActionSchema | None: The actions for the belt timer, or None if the user may not manage it.
    """
    if not General.objects.has_basic_access(request.user):
        return None

    perms = get_manage_belt_timer_or_none(request=request, timer_pk=timer.pk)[0]
    if not perms:
        return None

    return schema.ActionSchema(
        update=schema.ModalSchema(
            url=reverse(
                "beltradar:api:modify_belt_timer",
                kwargs={"timer_id": timer.pk},
            ),
            modal_id="beltradar-accept-modify-belt-timer",
        ),
        delete=schema.ModalSchema(
            url=reverse(
                "beltradar:api:delete_belt_timer", kwargs={"timer_id": timer.pk}
            ),
            modal_id="beltradar-accept-delete-belt-timer",
        ),
    )


def get_snapshot_add_action(
    request: WSGIRequest, public_id: str  # pylint: disable=unused-argument
) -> schema.ModalSchema | None:
    """
    Get the action for adding a snapshot to a session.

    Args:
        request (WSGIRequest): The HTTP request object.
        public_id (str): The public ID of the snapshot's session.
    Returns:
        schema.ModalSchema | None: The action, or None if the user may not access the session.
    """
    perms = get_session_or_none(request=request, public_id=public_id)[0]
    if not perms:
        return None

    return schema.ModalSchema(
        url=reverse("beltradar:api:add_snapshot", kwargs={"public_id": public_id}),
        modal_id="beltradar-add-snapshot",
    )


def get_snapshot_delete_action(
    request: WSGIRequest,
    public_id: str,
    identifier: str = None,
) -> schema.ModalSchema | None:
    """
    Get the action for deleting a snapshot of a session.

    Args:
        request (WSGIRequest): The HTTP request object.
        public_id (str): The public ID of the session.
        identifier (str): The snapshot identifier. If not provided, the last snapshot is used.
    Returns:
        schema.ModalSchema | None: The action, or None if the user may not manage the session.
    """
    perms, session = get_manage_session_or_none(request=request, public_id=public_id)
    if not perms:
        return None

    if identifier is None:
        try:
            identifier = session.br_snapshots.last().identifier
        except AttributeError:
            return None

    return schema.ModalSchema(
        url=reverse(
            "beltradar:api:delete_snapshot",
            kwargs={"public_id": public_id, "identifier": identifier},
        ),
        modal_id="beltradar-accept-delete-snapshot",
    )
