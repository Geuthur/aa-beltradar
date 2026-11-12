# Standard Library
import ast
from pathlib import Path
from unittest.mock import patch

# Django
from django.test import TestCase

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter

# AA Belt Radar
import beltradar
from beltradar.models import BeltSurveySession, General
from beltradar.tests import AuthTestCase
from beltradar.tests.testdata.beltradar import UserMainFactory

PERMISSION_CALLS = {
    "has_perm",
    "has_perms",
    "permission_required",
    "permissions_required",
}


def _call_name(node: ast.Call) -> str:
    """Return the name of the called function or method."""
    func = node.func
    if isinstance(func, ast.Attribute):
        return func.attr
    if isinstance(func, ast.Name):
        return func.id
    return ""


def _used_permissions() -> dict[str, set[str]]:
    """Return all permission strings passed to permission checks, with the files using them."""
    used: dict[str, set[str]] = {}
    root = Path(beltradar.__file__).parent
    for path in root.rglob("*.py"):
        relative = path.relative_to(root)
        if "tests" in relative.parts or "migrations" in relative.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and _call_name(node) in PERMISSION_CALLS:
                for arg in node.args:
                    for sub in ast.walk(arg):
                        if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                            used.setdefault(sub.value, set()).add(str(relative))
    return used


class TestPermissionStrings(TestCase):
    """Test that every permission string used in the code is defined in General."""

    def test_should_find_permission_strings_in_code(self):
        self.assertTrue(_used_permissions())

    def test_used_permissions_should_be_defined_in_general(self):
        defined = {
            f"{General._meta.app_label}.{codename}"
            for codename, _label in General._meta.permissions
        }
        for permission, files in _used_permissions().items():
            with self.subTest(permission=permission):
                self.assertIn(
                    permission, defined, msg=f"Unknown permission used in {files}"
                )

    def test_codenames_should_stay_unchanged(self):
        self.assertListEqual(
            [codename for codename, _label in General._meta.permissions],
            ["basic_access", "manage_access", "admin_access"],
        )


class TestGeneralManager(AuthTestCase):
    """Test the app rules of the GeneralManager."""

    def test_has_management_access_should_accept_manage_and_admin(self):
        for permission, expected in (
            ("beltradar.manage_access", True),
            ("beltradar.admin_access", True),
            ("beltradar.basic_access", False),
        ):
            with self.subTest(permission=permission):
                user = UserMainFactory(permissions=[permission])
                self.assertEqual(General.objects.has_management_access(user), expected)

    def test_has_basic_access_should_accept_only_basic_access(self):
        for permission, expected in (
            ("beltradar.basic_access", True),
            ("beltradar.manage_access", False),
            ("beltradar.admin_access", False),
        ):
            with self.subTest(permission=permission):
                user = UserMainFactory(permissions=[permission])
                self.assertEqual(General.objects.has_basic_access(user), expected)

    def test_has_basic_access_should_accept_superuser(self):
        self.assertTrue(General.objects.has_basic_access(self.superuser))

    def test_has_admin_access_should_accept_superuser_and_admin_access(self):
        for user, expected in (
            (self.superuser, True),
            (UserMainFactory(permissions=["beltradar.admin_access"]), True),
            (UserMainFactory(permissions=["beltradar.manage_access"]), False),
            (UserMainFactory(permissions=["beltradar.basic_access"]), False),
        ):
            with self.subTest(user=user):
                self.assertEqual(General.objects.has_admin_access(user), expected)


class TestAccessUsesGeneralManager(AuthTestCase):
    """The access querysets ask the GeneralManager and only filter rows."""

    def test_visible_to_and_manage_to_should_ask_general_manager(self):
        for method in ("visible_to", "manage_to"):
            with self.subTest(method=method):
                with patch.object(
                    General.objects, "has_admin_access", return_value=True
                ) as admin_check:
                    result = getattr(BeltSurveySession.objects, method)(self.user)
                admin_check.assert_called_once_with(self.user)
                self.assertEqual(result.count(), BeltSurveySession.objects.count())

    def test_visible_eve_characters_should_ask_general_manager(self):
        with patch.object(
            General.objects, "has_admin_access", return_value=True
        ) as admin_check:
            result = BeltSurveySession.objects.visible_eve_characters(self.user)
        admin_check.assert_called_once_with(self.user)
        self.assertEqual(result.count(), EveCharacter.objects.count())
