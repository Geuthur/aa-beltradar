# Third Party
from ninja import Schema

# Django
from django.utils import timezone


class BeltSurveySessionSchema(Schema):
    public_id: str
    name: str
    created_at: timezone.datetime
    owner: str
    html: str | None = None


class OreSchema(Schema):
    portrait: str | None = None
    name: str
    units: int
    volume_m3: int
    price_isk: float
    price_compressed: float | None = None
    timestamp: timezone.datetime
    snapshot: str
    html: str | None = None


class OreMiningChartSeriesSchema(Schema):
    name: str
    data: list[float]


class OreMiningChartItemSchema(Schema):
    ore_name: str
    start_volume: float = 0.0
    volume_left: float = 0.0
    volume_mined: float = 0.0
    progress_percent: float = 0.0
    rate_m3_per_s: float = 0.0
    eta_seconds: float | None = None


class OreChartDataSchema(Schema):
    categories: list[str] = []
    series: list[OreMiningChartSeriesSchema] = []
    items: list[OreMiningChartItemSchema] = []


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
    session_name: str
    session_created_at: timezone.datetime
    session_owner: str
    snapshot: str
    timestamp: timezone.datetime
    entries: list[OreSchema]
    charts: OreChartDataSchema | None = None
    stats: SnapShotStatsSchema | None = None
    delete_html: str | None = None
