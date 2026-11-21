# Standard Library
from decimal import Decimal

# Third Party
import pook
from evesde_factory.allianceauth import EveCharacterFactory, UserFactory
from evesde_factory.eve_sde import ItemTypeFactory
from evesde_factory.utils import add_character_to_user

# Django
from django.utils import timezone

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter

# AA Belt Radar
from beltradar.models import BeltSurveySession, BeltTimer, EveMarketPrice
from beltradar.tests import AuthTestCase
from beltradar.tests.testdata.beltradar import (
    BeltSessionFactory,
    BeltTimerFactory,
    UserMainFactory,
)


class TestAccessQuerySetAdminAccess(AuthTestCase):
    """Test that admin scope of visible_to and manage_to depends on beltradar.admin_access."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.admin = UserMainFactory(
            permissions=["beltradar.basic_access", "beltradar.admin_access"]
        )
        cls.own_session = BeltSessionFactory(owner=cls.user)
        cls.foreign_private_session = BeltSessionFactory(is_public=False)
        cls.foreign_public_session = BeltSessionFactory(is_public=True)

    def test_visible_to_should_return_all_sessions_for_admin(self):
        # when
        result = BeltSurveySession.objects.visible_to(self.admin)
        # then
        self.assertSetEqual(
            set(result),
            {
                self.own_session,
                self.foreign_private_session,
                self.foreign_public_session,
            },
        )

    def test_visible_to_should_not_return_foreign_private_sessions_for_basic_user(
        self,
    ):
        # when
        result = BeltSurveySession.objects.visible_to(self.user)
        # then
        self.assertSetEqual(
            set(result), {self.own_session, self.foreign_public_session}
        )

    def test_manage_to_should_return_all_sessions_for_admin(self):
        # when
        result = BeltSurveySession.objects.manage_to(self.admin)
        # then
        self.assertSetEqual(
            set(result),
            {
                self.own_session,
                self.foreign_private_session,
                self.foreign_public_session,
            },
        )

    def test_manage_to_should_return_only_own_sessions_for_basic_user(self):
        # when
        result = BeltSurveySession.objects.manage_to(self.user)
        # then
        self.assertSetEqual(set(result), {self.own_session})


class TestAccessRules(AuthTestCase):
    """Test visible_to and manage_to of sessions and timers for every kind of user."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.admin = UserMainFactory(
            permissions=["beltradar.basic_access", "beltradar.admin_access"]
        )
        cls.manager = UserMainFactory(
            permissions=["beltradar.basic_access", "beltradar.manage_access"]
        )
        cls.no_main = UserFactory(permissions=["beltradar.basic_access"])
        cls.objs = {}
        for model, obj_factory in (
            (BeltSurveySession, BeltSessionFactory),
            (BeltTimer, BeltTimerFactory),
        ):
            cls.objs[model] = {
                "own": obj_factory(owner=cls.user),
                "own_public": obj_factory(owner=cls.user, is_public=True),
                "foreign_private": obj_factory(is_public=False),
                "foreign_public": obj_factory(is_public=True),
                "no_main_own": obj_factory(owner=cls.no_main),
            }

    def _assert_objs(self, model, result, keys):
        self.assertSetEqual(set(result), {self.objs[model][key] for key in keys})
        # no duplicates
        self.assertEqual(result.count(), len(keys))

    def test_setup_should_have_user_without_main_character(self):
        self.assertIsNone(self.no_main.profile.main_character)

    def test_visible_to_should_return_everything_for_admin_and_superuser(self):
        for model in self.objs:
            for user in (self.admin, self.superuser):
                with self.subTest(model=model, user=user):
                    self._assert_objs(
                        model, model.objects.visible_to(user), self.objs[model]
                    )

    def test_manage_to_should_return_everything_for_admin_and_superuser(self):
        for model in self.objs:
            for user in (self.admin, self.superuser):
                with self.subTest(model=model, user=user):
                    self._assert_objs(
                        model, model.objects.manage_to(user), self.objs[model]
                    )

    def test_visible_to_should_return_own_and_public_for_owner(self):
        for model in self.objs:
            with self.subTest(model=model):
                self._assert_objs(
                    model,
                    model.objects.visible_to(self.user),
                    ["own", "own_public", "foreign_public"],
                )

    def test_manage_to_should_return_only_own_for_owner(self):
        for model in self.objs:
            with self.subTest(model=model):
                self._assert_objs(
                    model, model.objects.manage_to(self.user), ["own", "own_public"]
                )

    def test_visible_to_should_return_only_public_for_foreign_user(self):
        """manage_access alone gives no wider scope."""
        for model in self.objs:
            with self.subTest(model=model):
                self._assert_objs(
                    model,
                    model.objects.visible_to(self.manager),
                    ["own_public", "foreign_public"],
                )

    def test_manage_to_should_return_nothing_for_foreign_user(self):
        for model in self.objs:
            with self.subTest(model=model):
                self._assert_objs(model, model.objects.manage_to(self.manager), [])

    def test_should_return_nothing_without_main_character(self):
        """Neither own nor public objects without a main character."""
        for model in self.objs:
            for method in ("visible_to", "manage_to"):
                with self.subTest(model=model, method=method):
                    result = getattr(model.objects, method)(self.no_main)
                    self._assert_objs(model, result, [])

    def test_should_return_everything_for_admin_without_main_character(self):
        """The admin rule is checked before the main character."""
        admin_no_main = UserFactory(
            permissions=["beltradar.basic_access", "beltradar.admin_access"]
        )
        superuser_no_main = UserFactory(permissions=[])
        superuser_no_main.is_superuser = True
        superuser_no_main.save()
        for model in self.objs:
            for user in (admin_no_main, superuser_no_main):
                for method in ("visible_to", "manage_to"):
                    with self.subTest(model=model, user=user, method=method):
                        result = getattr(model.objects, method)(user)
                        self._assert_objs(model, result, self.objs[model])

    def test_should_restrict_an_already_filtered_queryset(self):
        """The queryset methods keep earlier filters."""
        for model in self.objs:
            with self.subTest(model=model):
                queryset = model.objects.get_queryset().filter(is_public=False)
                self._assert_objs(model, queryset.visible_to(self.user), ["own"])
                self._assert_objs(model, queryset.manage_to(self.user), ["own"])
                self._assert_objs(
                    model,
                    queryset.visible_to(self.admin),
                    ["own", "foreign_private", "no_main_own"],
                )


class TestVisibleEveCharacters(AuthTestCase):
    """Test visible_eve_characters of sessions and timers for every kind of user."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.admin = UserMainFactory(
            permissions=["beltradar.basic_access", "beltradar.admin_access"]
        )
        cls.alt = EveCharacterFactory()
        add_character_to_user(user=cls.user, character=cls.alt)
        cls.unowned = EveCharacterFactory()
        cls.no_main = UserFactory(permissions=["beltradar.basic_access"])
        cls.no_main_character = EveCharacterFactory()
        add_character_to_user(user=cls.no_main, character=cls.no_main_character)

    def test_setup_should_have_user_without_main_character(self):
        self.assertIsNone(self.no_main.profile.main_character)
        self.assertTrue(
            self.no_main.character_ownerships.filter(
                character=self.no_main_character
            ).exists()
        )

    def test_should_return_all_characters_for_admin_and_superuser(self):
        for manager in (BeltSurveySession.objects, BeltTimer.objects):
            for user in (self.admin, self.superuser):
                with self.subTest(manager=manager, user=user):
                    result = manager.visible_eve_characters(user)
                    self.assertSetEqual(set(result), set(EveCharacter.objects.all()))
                    self.assertIn(self.unowned, result)

    def test_should_return_only_own_characters_for_user(self):
        for manager in (BeltSurveySession.objects, BeltTimer.objects):
            with self.subTest(manager=manager):
                result = manager.visible_eve_characters(self.user)
                self.assertSetEqual(
                    set(result), {self.user.profile.main_character, self.alt}
                )
                self.assertEqual(result.count(), 2)

    def test_should_return_nothing_without_main_character(self):
        for manager in (BeltSurveySession.objects, BeltTimer.objects):
            with self.subTest(manager=manager):
                result = manager.visible_eve_characters(self.no_main)
                self.assertEqual(result.count(), 0)


class TestEveMarketPriceManagerUpdateFromEsi(AuthTestCase):
    """Test EveMarketPrice.objects.update_from_esi against the ESI endpoint."""

    ESI_URL = "https://esi.evetech.net/markets/prices"

    @pook.on
    def test_should_create_price_without_adjusted_price(self):
        # given
        eve_type = ItemTypeFactory()
        pook.get(
            self.ESI_URL,
            reply=200,
            response_json=[{"average_price": 150.5, "type_id": eve_type.id}],
        )
        # when
        result = EveMarketPrice.objects.update_from_esi()
        # then
        self.assertEqual(result, 1)
        price = EveMarketPrice.objects.get(eve_type=eve_type)
        self.assertEqual(price.average_price, Decimal("150.50"))
        self.assertIsNone(price.adjusted_price)

    @pook.on
    def test_should_update_price_without_adjusted_price(self):
        # given
        eve_type = ItemTypeFactory()
        EveMarketPrice.objects.create(
            eve_type=eve_type,
            average_price=Decimal("100.00"),
            adjusted_price=Decimal("90.00"),
            updated_at=timezone.now(),
        )
        pook.get(
            self.ESI_URL,
            reply=200,
            response_json=[{"average_price": 150.5, "type_id": eve_type.id}],
        )
        # when
        result = EveMarketPrice.objects.update_from_esi()
        # then
        self.assertEqual(result, 1)
        price = EveMarketPrice.objects.get(eve_type=eve_type)
        self.assertEqual(price.average_price, Decimal("150.50"))
        self.assertIsNone(price.adjusted_price)

    @pook.on
    def test_should_skip_unknown_type_and_store_known_types(self):
        # given
        known_type = ItemTypeFactory()
        new_type = ItemTypeFactory()
        unknown_type_id = new_type.id + 1000
        EveMarketPrice.objects.create(
            eve_type=known_type,
            average_price=Decimal("100.00"),
            adjusted_price=Decimal("90.00"),
            updated_at=timezone.now(),
        )
        pook.get(
            self.ESI_URL,
            reply=200,
            response_json=[
                {
                    "adjusted_price": 190.0,
                    "average_price": 200.0,
                    "type_id": known_type.id,
                },
                {
                    "adjusted_price": 290.0,
                    "average_price": 300.0,
                    "type_id": unknown_type_id,
                },
                {
                    "adjusted_price": 390.0,
                    "average_price": 400.0,
                    "type_id": new_type.id,
                },
            ],
        )
        # when
        result = EveMarketPrice.objects.update_from_esi()
        # then
        self.assertEqual(result, 2)
        self.assertEqual(
            EveMarketPrice.objects.get(eve_type=known_type).average_price,
            Decimal("200.00"),
        )
        self.assertEqual(
            EveMarketPrice.objects.get(eve_type=new_type).average_price,
            Decimal("400.00"),
        )
        self.assertFalse(
            EveMarketPrice.objects.filter(eve_type_id=unknown_type_id).exists()
        )
