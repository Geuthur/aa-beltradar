# Standard Library
from typing import Any

# Third Party
from ninja import Schema

# Django
from django.utils import timezone


class UserData(Schema):
    """
    Schema for user data, including character ID and character name.

    Parameters:
        user_id (int): The ID of the user.
        character_id (int): The ID of the character associated with the user.
        character_name (str): The name of the character.
        portrait (str | None): The URL or path to the character's portrait image.
        notification (boolean): The notification status for the user.
    """

    user_id: int
    character_id: int
    character_name: str
    portrait: str | None = None

    notification: bool


class DataTableSchema(Schema):
    raw: Any
    display: str
    sort: str | None = None
    translation: str | None = None
    dropdown_text: str | None = None


class ModalSchema(Schema):
    """Schema for modal dialog data."""

    title: str
    text: str
    icon: str
    modal_id: str
    url: str
    color: str | None = None
    buttonText: str | None = None


class ActionSchema(Schema):
    """
    Schema for actions related to a session, including create, delete, and update actions.

    Parameters:
        create (str | None): The action for creating a session.
        delete (str | None): The action for deleting a session.
        update (str | None): The action for updating a session.
    """

    create: ModalSchema | None = None
    delete: ModalSchema | None = None
    update: ModalSchema | None = None


class OwnerSchema(Schema):
    character_id: int = 0
    character_name: str | None = None
    portrait: str | None = None


class SessionStatsSchema(Schema):
    belt_volume: float = 0.0
    belt_volume_left_m3: float = 0.0
    remaining_asteroids: int = 0
    total_asteroids: int = 0
    progress_percent: float = 0.0
    duration_seconds: float = 0.0
    mining_rate_m3_per_s: float = 0.0
    finish_eta: timezone.datetime | None = None
    expected_belt_type: str | None = None
    expected_belt_size: str | None = None


class SessionSchema(Schema):
    public_id: str
    name: str
    owner: OwnerSchema
    created_at: timezone.datetime
    public: DataTableSchema
    first_timestamp: timezone.datetime | None = None
    last_timestamp: timezone.datetime | None = None
    total_timestamps: int | None = None
    stats: SessionStatsSchema | None = None
    actions: ActionSchema | None = None


class BeltSurveySessionSchema(Schema):
    public_id: str
    name: str
    created_at: timezone.datetime
    owner: OwnerSchema
    public: DataTableSchema
    actions: ActionSchema | None = None
    html: str | None = None


class BeltTimerSchema(Schema):
    public_id: str
    belt_id: str
    belt_name: str
    belt_size: str
    belt_type: str
    eta: DataTableSchema
    public: DataTableSchema
    is_expired: bool | None = None
    has_session: bool = False
    actions: ActionSchema | None = None
    html: str | None = None


class OreSchema(Schema):
    portrait: str | None = None
    name: str
    units: int
    volume_m3: int
    price_isk: float
    price_compressed: float | None = None
    income_per_h: float | None = None
    income_cmp_per_h: float | None = None
    html: str | None = None


class OreSchemaResponse(Schema):
    errors: list[str] = []
    ore_list: list[OreSchema] = []


class ApexChartSeriesDataSchema(Schema):
    name: str
    data: list[float]
    type: str | None = None


class ApexChartSchema(Schema):
    categories: list[str] = []
    series: list[ApexChartSeriesDataSchema] = []


class SnapShotDataSchema(Schema):
    identifier: str
    last_timestamp: timezone.datetime | None = None
    first_timestamp: timezone.datetime | None = None


class SnapShotSchema(Schema):
    snapshot: SnapShotDataSchema | None = None
    ore_list: list[OreSchema] | None = None
    charts: ApexChartSchema | None = None
    traffic: ApexChartSchema | None = None
    actions: ActionSchema | None = None


class MenuLink(Schema):
    """
    Represents a link in the menu.

    Parameters:
        name (str): The name of the menu link.
        link (str | None): The URL or path the menu link points to.
    """

    name: str
    link: str = None


class MenuCategory(MenuLink):
    """
    Represents a category in the menu, which can contain multiple links.

    Parameters:
        links (list[MenuLink]): A list of links under this category.
        name (str): The name of the menu category.
        link (str | None): The optional link for the menu category.
    """

    links: list[MenuLink] = None


class MenuModalSchema(Schema):
    create_session: ModalSchema | None = None
    create_belt_timer: ModalSchema | None = None
    create_snapshot: ModalSchema | None = None


class MenuSchema(Schema):
    links: list[MenuLink] = []
    modals: MenuModalSchema | None = None


class CreateSessionSchema(Schema):
    name: str
    is_public: DataTableSchema
