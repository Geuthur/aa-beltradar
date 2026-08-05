# Third Party
import factory

# AA Belt Radar
from beltradar.models import BeltSurveyEntry, BeltSurveySession, BeltTimer
from beltradar.models.helper.choices import BeltSizeChoice, BeltTypeChoice
from beltradar.tests.testdata.factory import (
    BaseMetaFactory,
    EveCharacterFactory,
    ItemTypeFactory,
    UserFactory,
)
from beltradar.tests.testdata.utils import add_character_to_user


class UserMainFactory(UserFactory):
    """Generate a User object with a main character and default permissions for Belt Radar."""

    permissions__ = ["beltradar.basic_access"]
    scopes__ = ["publicData"]

    @factory.post_generation
    def main_character(obj, create, _, **kwargs):
        if not create:
            return
        if "character" in kwargs:
            character = kwargs["character"]
        else:
            character_name = f"{obj.first_name} {obj.last_name}"
            character = EveCharacterFactory(character_name=character_name)

        add_character_to_user(
            user=obj,
            character=character,
            is_main=True,
            scopes=obj._main_character_scopes,
        )


class BeltSessionFactory(
    factory.django.DjangoModelFactory, metaclass=BaseMetaFactory[BeltSurveySession]
):
    """Generate a BeltSurveySession object with default values."""

    class Meta:
        model = BeltSurveySession
        django_get_or_create = ("public_id", "owner")

    owner = factory.SubFactory(UserMainFactory)
    public_id = factory.Faker("uuid4")
    name = factory.Faker("sentence", nb_words=3)
    created_at = factory.Faker("date_time_this_year", tzinfo=None)


class BeltSurveyEntryFactory(
    factory.django.DjangoModelFactory, metaclass=BaseMetaFactory[BeltSurveyEntry]
):
    """Generate a BeltSurveyEntry object with default values."""

    class Meta:
        model = BeltSurveyEntry
        django_get_or_create = ("session", "snapshot", "timestamp", "eve_type")

    session = factory.SubFactory(BeltSessionFactory)
    snapshot = factory.Faker("sha256")
    recorded_by = factory.SubFactory(UserMainFactory)
    timestamp = factory.Faker("date_time_this_year", tzinfo=None)
    eve_type = factory.SubFactory(ItemTypeFactory)
    units = factory.Faker("random_int", min=1, max=1000)
    volume_left = factory.Faker("random_int", min=1, max=10000)
    note = None
    price_compressed = None
    price = None


class BeltTimerFactory(
    factory.django.DjangoModelFactory, metaclass=BaseMetaFactory[BeltTimer]
):
    """Generate a BeltTimer object with default values."""

    class Meta:
        model = BeltTimer
        django_get_or_create = ("owner", "public_id")

    owner = factory.SubFactory(UserMainFactory)
    public_id = factory.Faker("uuid4")
    belt_id = factory.Faker("random_int", min=1, max=100)
    belt_name = factory.Faker("word")
    belt_size = factory.Faker(
        "random_element", elements=[choice[0] for choice in BeltSizeChoice.choices]
    )
    belt_type = factory.Faker(
        "random_element", elements=[choice[0] for choice in BeltTypeChoice.choices]
    )
    eta = None
    public = False
    sent_notification = False
