# Standard Library
from typing import Any

# Third Party
from ninja import Schema

# Django
from django.utils import timezone


class DataTableSchema(Schema):
    raw: Any
    display: str
    sort: str | None = None
    translation: str | None = None
    dropdown_text: str | None = None


class ActionSchema(Schema):
    """
    Schema for actions related to a session, including create, delete, and update actions.

    Parameters:
        create (str | None): The action for creating a session.
        delete (str | None): The action for deleting a session.
        update (str | None): The action for updating a session.
    """

    create: str | None = None
    delete: str | None = None
    update: str | None = None


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
    owner: str
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
    owner: str
    public: DataTableSchema
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
