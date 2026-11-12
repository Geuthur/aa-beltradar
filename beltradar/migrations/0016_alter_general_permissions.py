# Django
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("beltradar", "0015_alter_usersettings_user"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="general",
            options={
                "default_permissions": (),
                "managed": False,
                "permissions": [
                    ("basic_access", "Can access this app, Belt Radar"),
                    ("manage_access", "Can manage Belt Radar"),
                    ("admin_access", "Admin access to Belt Radar"),
                ],
                "verbose_name": "AA-Belt-Radar",
                "verbose_name_plural": "AA-Belt-Radar",
            },
        ),
    ]
