# Third Party
from ninja import Schema


class ExampleSchema(Schema):
    character_id: int | None = None
    character_name: str | None = None
    corporation_id: int | None = None
    corporation_name: str | None = None
