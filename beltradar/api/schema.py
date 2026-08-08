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


class SessionSchema(Schema):
    public_id: str
    name: str
    created_at: timezone.datetime
    owner: str
    first_entry_timestamp: timezone.datetime | None = None
    last_entry_timestamp: timezone.datetime | None = None


class BeltSurveySessionSchema(Schema):
    public_id: str
    name: str
    created_at: timezone.datetime
    owner: str
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
    timestamp: timezone.datetime
    snapshot: str
    html: str | None = None


class OreSchemaResponse(Schema):
    errors: list[str] = []
    entries: list[OreSchema] = []


class ApexChartSeriesDataSchema(Schema):
    name: str
    data: list[float]
    type: str | None = None


class ApexChartSchema(Schema):
    categories: list[str] = []
    series: list[ApexChartSeriesDataSchema] = []


class SnapShotStatsSchema(Schema):
    belt_volume: float = 0.0
    belt_volume_left_m3: float = 0.0
    remaining_asteroids: int = 0
    total_asteroids: int = 0
    progress_percent: float = 0.0
    duration_seconds: float = 0.0
    mining_rate_m3_per_s: float = 0.0
    finish_eta: timezone.datetime | None = None


class SnapShotSchema(Schema):
    session: SessionSchema
    snapshot: str | None = None
    entries: list[OreSchema]
    charts: ApexChartSchema | None = None
    traffic: ApexChartSchema | None = None
    stats: SnapShotStatsSchema | None = None
    delete_html: str | None = None
