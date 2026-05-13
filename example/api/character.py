# Third Party
from ninja import NinjaAPI

# Django
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# AA Example
from example import __title__
from example.api import schema
from example.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


class CharacterApiEndpoints:
    tags = ["Example"]

    def __init__(self, api: NinjaAPI):
        @api.get(
            "example/",
            response={200: list[schema.ExampleSchema], 403: str},
            tags=self.tags,
        )
        def get_example(request):
            """Get Example Data"""
            user = request.user
            if not user.is_superuser:
                return 403, _("You do not have permission to access this resource.")

            # Example data - replace this with your actual logic
            example_data = [
                schema.ExampleSchema(
                    id=1,
                    name="Example 1",
                    description="This is an example.",
                ),
                schema.ExampleSchema(
                    id=2,
                    name="Example 2",
                    description="This is another example.",
                ),
            ]

            return 200, example_data
