"""Test to ensure that the factories are working correctly."""

# AA Belt Radar
from beltradar.tests import BeltRadarTestCase
from beltradar.tests.testdata.beltradar import (
    BeltSessionFactory,
    BeltSurveyEntryFactory,
    BeltSurveySnapshotFactory,
    UserMainFactory,
)
from beltradar.tests.testdata.factory import (
    ConstellationFactory,
    EveAllianceInfoFactory,
    EveCharacterFactory,
    EveCorporationInfoFactory,
    ItemCategoryFactory,
    ItemGroupFactory,
    ItemTypeFactory,
    RegionFactory,
    SolarSystemFactory,
)


class TestFactory(BeltRadarTestCase):
    """Test the factories."""

    def test_can_create_user(self):
        """Test that a user can be created."""
        user = UserMainFactory()
        self.assertTrue(user.has_perm("beltradar.basic_access"))

    def test_can_create_belt_session(self):
        """Test that a belt session can be created."""
        session = BeltSessionFactory()
        self.assertTrue(session)

    def test_can_create_belt_session_for_given_user(self):
        """Test that a belt session can be created."""
        session = BeltSessionFactory(owner=self.user)
        self.assertEqual(session.owner, self.user)

    def test_can_create_belt_snapshot(self):
        """Test that a belt survey snapshot can be created."""
        snapshot = BeltSurveySnapshotFactory()
        self.assertTrue(snapshot)

    def test_can_create_belt_snapshot_for_given_session(self):
        """Test that a belt survey snapshot can be created for a given session."""
        session = BeltSessionFactory()
        snapshot = BeltSurveySnapshotFactory(session=session)
        self.assertEqual(snapshot.session, session)

    def test_can_create_belt_survey_entry(self):
        """Test that a belt survey entry can be created."""
        entry = BeltSurveyEntryFactory()
        self.assertTrue(entry)

    def test_can_create_belt_survey_entry_for_given_snapshot(self):
        """Test that a belt survey entry can be created for a given snapshot."""
        snapshot = BeltSurveySnapshotFactory()
        entry = BeltSurveyEntryFactory(snapshot=snapshot)
        self.assertEqual(entry.snapshot.session, snapshot.session)

    def test_can_create_eve_character(self):
        """Test that an EVE character can be created."""
        character = EveCharacterFactory()
        self.assertIsNotNone(character.character_id)

    def test_can_create_eve_corporation(self):
        """Test that an EVE corporation can be created."""
        corporation = EveCorporationInfoFactory()
        self.assertIsNotNone(corporation.corporation_id)

    def test_can_create_eve_alliance(self):
        """Test that an EVE alliance can be created."""
        alliance = EveAllianceInfoFactory()
        self.assertIsNotNone(alliance.alliance_id)

    def test_can_create_item_type(self):
        """Test that an item type can be created."""
        item_type = ItemTypeFactory()
        self.assertIsNotNone(item_type.id)

    def test_can_create_item_group(self):
        """Test that an item group can be created."""
        item_group = ItemGroupFactory()
        self.assertIsNotNone(item_group.id)

    def test_can_create_item_category(self):
        """Test that an item category can be created."""
        item_category = ItemCategoryFactory()
        self.assertIsNotNone(item_category.id)

    def test_can_create_region(self):
        """Test that a region can be created."""
        region = RegionFactory()
        self.assertIsNotNone(region.id)

    def test_can_create_constellation(self):
        """Test that a constellation can be created."""
        constellation = ConstellationFactory()
        self.assertIsNotNone(constellation.id)

    def test_can_create_solar_system(self):
        """Test that a solar system can be created."""
        solar_system = SolarSystemFactory()
        self.assertIsNotNone(solar_system.id)
