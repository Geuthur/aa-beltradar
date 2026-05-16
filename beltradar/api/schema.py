# Third Party
from ninja import Schema

# Django
from django.utils import timezone


class CharacterSchema(Schema):
    character_id: int | None = None
    character_name: str | None = None
    character_portrait: str | None = None
    corporation_id: int | None = None
    corporation_name: str | None = None


class CorporationSchema(Schema):
    corporation_id: int | None = None
    corporation_name: str | None = None
    corporation_logo: str | None = None


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


class BeltSurveySessionSchema(Schema):
    public_id: str
    name: str
    created_at: timezone.datetime
    owner: str
    html: str | None = None


class OreSchemaList(Schema):
    snapshot: str | None = None
    timestamp: timezone.datetime | None = None
    entries: list[OreSchema]
    delete_html: str | None = None


class SurveyStatsSchema(Schema):
    size: float = 0.0
    left: float = 0.0
    mined: float = 0.0
    duration: float = 0.0
    start: timezone.datetime | None = None
    end: timezone.datetime | None = None
    rate: float = 0.0
    total_asteroids: int = 0
    remaining_asteroids: int = 0
    finish: timezone.datetime | None = None
    progress_percent: float = 0.0
