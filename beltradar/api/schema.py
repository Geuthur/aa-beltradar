# Third Party
from ninja import Schema


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
