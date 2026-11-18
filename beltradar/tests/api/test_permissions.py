# Standard Library
from http import HTTPStatus

# Third Party
from evesde_factory.eve_sde import ItemTypeFactory

# Django
from django.urls import reverse

# AA Belt Radar
from beltradar.api.helpers.actions import (
    get_snapshot_add_action,
    get_snapshot_delete_action,
)
from beltradar.models import BeltSurveySession, BeltTimer
from beltradar.models.beltradar import BeltSurveySnapshot
from beltradar.tests import AuthTestCase
from beltradar.tests.testdata.beltradar import (
    BeltSessionFactory,
    BeltSnapshotFactory,
    BeltSurveyEntryFactory,
    BeltTimerFactory,
    UserMainFactory,
)

API_URL = "beltradar:api"


class TestApiRequiresBasicAccess(AuthTestCase):
    """Every endpoint must reject users without `beltradar.basic_access`."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_no_permission = UserMainFactory(permissions__=[])
        cls.character_id = cls.user_no_permission.profile.main_character.character_id

    def test_get_menu_should_403(self):
        self.client.force_login(self.user_no_permission)

        response = self.client.get(reverse(f"{API_URL}:get_menu"))

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_snapshot_actions_should_be_none(self):
        session = BeltSessionFactory(owner=self.user_no_permission)
        snapshot = BeltSnapshotFactory(session=session)
        request = self.factory.get(reverse("beltradar:react_base"))
        request.user = self.user_no_permission

        self.assertIsNone(
            get_snapshot_add_action(request=request, public_id=session.public_id)
        )
        self.assertIsNone(
            get_snapshot_delete_action(
                request=request,
                public_id=session.public_id,
                identifier=snapshot.identifier,
            )
        )

    def test_get_public_sessions_should_403(self):
        BeltSessionFactory(owner=self.user, is_public=True)
        self.client.force_login(self.user_no_permission)

        response = self.client.get(reverse(f"{API_URL}:get_public_sessions"))

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_get_my_sessions_should_403(self):
        BeltSessionFactory(owner=self.user_no_permission)
        self.client.force_login(self.user_no_permission)

        response = self.client.get(
            reverse(
                f"{API_URL}:get_my_sessions",
                kwargs={"character_id": self.character_id},
            )
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_get_belt_timers_should_403(self):
        BeltTimerFactory(owner=self.user, is_public=True)
        self.client.force_login(self.user_no_permission)

        response = self.client.get(reverse(f"{API_URL}:get_belt_timers"))

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_get_my_belt_timer_should_403(self):
        BeltTimerFactory(owner=self.user_no_permission)
        self.client.force_login(self.user_no_permission)

        response = self.client.get(
            reverse(
                f"{API_URL}:get_my_belt_timer",
                kwargs={"character_id": self.character_id},
            )
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_delete_session_should_403_for_owner(self):
        session = BeltSessionFactory(owner=self.user_no_permission)
        self.client.force_login(self.user_no_permission)

        response = self.client.post(
            reverse(
                f"{API_URL}:delete_session", kwargs={"public_id": session.public_id}
            )
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertTrue(BeltSurveySession.objects.filter(pk=session.pk).exists())

    def test_modify_session_should_403_for_owner(self):
        session = BeltSessionFactory(owner=self.user_no_permission, is_public=False)
        self.client.force_login(self.user_no_permission)

        response = self.client.post(
            reverse(
                f"{API_URL}:modify_session",
                kwargs={
                    "public_id": session.public_id,
                    "field": "is_public",
                    "value": "True",
                },
            )
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        session.refresh_from_db()
        self.assertFalse(session.is_public)

    def test_delete_snapshot_should_403_for_owner(self):
        session = BeltSessionFactory(owner=self.user_no_permission)
        snapshot = BeltSnapshotFactory(session=session)
        self.client.force_login(self.user_no_permission)

        response = self.client.post(
            reverse(
                f"{API_URL}:delete_snapshot",
                kwargs={
                    "public_id": session.public_id,
                    "identifier": snapshot.identifier,
                },
            )
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertTrue(BeltSurveySnapshot.objects.filter(pk=snapshot.pk).exists())

    def test_add_snapshot_should_403_for_owner(self):
        session = BeltSessionFactory(owner=self.user_no_permission)
        self.client.force_login(self.user_no_permission)

        response = self.client.post(
            reverse(f"{API_URL}:add_snapshot", kwargs={"public_id": session.public_id}),
            data={"raw_data": "Veldspar\t100\t10 m3\t1 km"},
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(session.br_snapshots.count(), 0)

    def test_add_session_belt_timer_should_403_for_owner(self):
        session = BeltSessionFactory(owner=self.user_no_permission)
        self.client.force_login(self.user_no_permission)

        response = self.client.post(
            reverse(
                f"{API_URL}:add_session_belt_timer",
                kwargs={"public_id": session.public_id},
            )
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_delete_belt_timer_should_403_for_owner(self):
        timer = BeltTimerFactory(owner=self.user_no_permission)
        self.client.force_login(self.user_no_permission)

        response = self.client.post(
            reverse(f"{API_URL}:delete_belt_timer", kwargs={"timer_id": timer.pk})
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_modify_belt_timer_should_403_for_owner(self):
        timer = BeltTimerFactory(owner=self.user_no_permission)
        self.client.force_login(self.user_no_permission)

        response = self.client.post(
            reverse(f"{API_URL}:modify_belt_timer", kwargs={"timer_id": timer.pk})
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)


class TestApiManageForeignPublicSession(AuthTestCase):
    """Seeing a public session of someone else must not allow managing it."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.owner = UserMainFactory()

    def test_delete_session_should_403_for_foreign_public_session(self):
        session = BeltSessionFactory(owner=self.owner, is_public=True)
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                f"{API_URL}:delete_session", kwargs={"public_id": session.public_id}
            )
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertTrue(BeltSurveySession.objects.filter(pk=session.pk).exists())

    def test_modify_session_should_403_for_foreign_public_session(self):
        session = BeltSessionFactory(owner=self.owner, is_public=True)
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                f"{API_URL}:modify_session",
                kwargs={
                    "public_id": session.public_id,
                    "field": "is_public",
                    "value": "False",
                },
            )
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        session.refresh_from_db()
        self.assertTrue(session.is_public)

    def test_delete_snapshot_should_403_for_foreign_public_session(self):
        session = BeltSessionFactory(owner=self.owner, is_public=True)
        snapshot = BeltSnapshotFactory(session=session)
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                f"{API_URL}:delete_snapshot",
                kwargs={
                    "public_id": session.public_id,
                    "identifier": snapshot.identifier,
                },
            )
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertTrue(BeltSurveySnapshot.objects.filter(pk=snapshot.pk).exists())

    def test_add_session_belt_timer_should_403_for_foreign_public_session(self):
        session = BeltSessionFactory(owner=self.owner, is_public=True)
        snapshot = BeltSnapshotFactory(session=session, recorded_by=self.owner)
        BeltSurveyEntryFactory(
            snapshot=snapshot, eve_type=ItemTypeFactory(name="Arkonor")
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                f"{API_URL}:add_session_belt_timer",
                kwargs={"public_id": session.public_id},
            )
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertFalse(BeltTimer.objects.filter(session=session).exists())

    def test_add_snapshot_should_200_for_foreign_public_session(self):
        """Shared surveying: everyone who sees a public session may add snapshots."""
        ItemTypeFactory(name="Gneiss IV-Grade")
        session = BeltSessionFactory(owner=self.owner, is_public=True)
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(f"{API_URL}:add_snapshot", kwargs={"public_id": session.public_id}),
            data={
                "raw_data": "Gneiss IV-Grade*\t1\xa0040\t5\xa0200 m3\t1\xa0860\xa0000,00 ISK\t501 km\n"
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(session.br_snapshots.get().recorded_by, self.user)

    def test_add_snapshot_should_403_for_foreign_private_session(self):
        session = BeltSessionFactory(owner=self.owner, is_public=False)
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(f"{API_URL}:add_snapshot", kwargs={"public_id": session.public_id}),
            data={"raw_data": "Gneiss IV-Grade*\t1\t5 m3\t1 ISK\t501 km\n"},
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(session.br_snapshots.count(), 0)

    def test_delete_session_should_200_for_owner(self):
        session = BeltSessionFactory(owner=self.user, is_public=True)
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                f"{API_URL}:delete_session", kwargs={"public_id": session.public_id}
            )
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(BeltSurveySession.objects.filter(pk=session.pk).exists())

    def test_delete_session_should_200_for_superuser(self):
        session = BeltSessionFactory(owner=self.owner, is_public=False)
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse(
                f"{API_URL}:delete_session", kwargs={"public_id": session.public_id}
            )
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_delete_session_should_404_for_unknown_session(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(f"{API_URL}:delete_session", kwargs={"public_id": "unknown"})
        )

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class TestApiModifySessionFields(AuthTestCase):
    """`modify_session` may only change `is_public`."""

    def _modify(self, session, field, value):
        return self.client.post(
            reverse(
                f"{API_URL}:modify_session",
                kwargs={
                    "public_id": session.public_id,
                    "field": field,
                    "value": value,
                },
            )
        )

    def test_modify_session_should_toggle_is_public(self):
        session = BeltSessionFactory(owner=self.user, is_public=False)
        self.client.force_login(self.user)

        response = self._modify(session, "is_public", "True")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        session.refresh_from_db()
        self.assertTrue(session.is_public)

        response = self._modify(session, "is_public", "False")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        session.refresh_from_db()
        self.assertFalse(session.is_public)

    def test_modify_session_should_400_for_other_fields(self):
        other_user = UserMainFactory()
        session = BeltSessionFactory(owner=self.user, name="Original")
        public_id = session.public_id
        self.client.force_login(self.user)

        for field, value in (
            ("name", "Changed"),
            ("public_id", "takeover"),
            ("owner_id", str(other_user.pk)),
            ("pk", "999999"),
        ):
            with self.subTest(field=field):
                response = self._modify(session, field, value)
                self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

        session = BeltSurveySession.objects.get(pk=session.pk)
        self.assertEqual(session.name, "Original")
        self.assertEqual(session.public_id, public_id)
        self.assertEqual(session.owner, self.user)

    def test_modify_session_should_400_for_invalid_value(self):
        session = BeltSessionFactory(owner=self.user, is_public=False)
        self.client.force_login(self.user)

        response = self._modify(session, "is_public", "maybe")

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        session.refresh_from_db()
        self.assertFalse(session.is_public)
