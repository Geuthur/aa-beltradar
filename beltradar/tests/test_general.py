# AA Belt Radar
from beltradar.models import General
from beltradar.tests import AuthTestCase
from beltradar.tests.testdata.beltradar import UserMainFactory


class TestGeneralPermissionHelpers(AuthTestCase):
    """Test the permission helpers of General."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.basic = UserMainFactory(permissions=["beltradar.basic_access"])
        cls.manager = UserMainFactory(
            permissions=["beltradar.basic_access", "beltradar.manage_access"]
        )
        cls.admin = UserMainFactory(
            permissions=["beltradar.basic_access", "beltradar.admin_access"]
        )

    def test_get_perm_should_return_full_permission_string(self):
        self.assertEqual(
            General.get_perm(General.Permission.BASIC_ACCESS), "beltradar.basic_access"
        )
        self.assertEqual(General.get_perm("manage_access"), "beltradar.manage_access")

    def test_permission_codenames_should_be_unchanged(self):
        self.assertListEqual(
            [codename for codename, _label in General._meta.permissions],
            ["basic_access", "manage_access", "admin_access"],
        )

    def test_has_perm_should_check_permission(self):
        self.assertTrue(General.has_perm(self.basic, General.Permission.BASIC_ACCESS))
        self.assertFalse(General.has_perm(self.basic, General.Permission.ADMIN_ACCESS))

    def test_has_perm_should_return_false_without_user(self):
        self.assertFalse(General.has_perm(None, General.Permission.BASIC_ACCESS))

    def test_has_any_perm_should_check_any_permission(self):
        self.assertTrue(
            General.has_any_perm(
                self.basic,
                General.Permission.MANAGE_ACCESS,
                General.Permission.BASIC_ACCESS,
            )
        )
        self.assertFalse(
            General.has_any_perm(
                self.basic,
                General.Permission.MANAGE_ACCESS,
                General.Permission.ADMIN_ACCESS,
            )
        )

    def test_has_management_access_should_accept_manage_and_admin(self):
        self.assertFalse(General.has_management_access(self.basic))
        self.assertTrue(General.has_management_access(self.manager))
        self.assertTrue(General.has_management_access(self.admin))
