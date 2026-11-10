# Django
from django.db import migrations


def remove_invalid_usersettings(apps, schema_editor):
    """Remove settings without a user and keep only the newest settings per user.

    `UserSettings.user` becomes a OneToOneField, so each user may only have
    one row left. The newest row (highest primary key) is kept.
    """
    UserSettings = apps.get_model("beltradar", "UserSettings")
    db_alias = schema_editor.connection.alias
    settings = UserSettings.objects.using(db_alias)

    settings.filter(user__isnull=True).delete()

    duplicate_ids = []
    seen_users = set()
    for pk, user_id in settings.order_by("user_id", "-pk").values_list("pk", "user_id"):
        if user_id in seen_users:
            duplicate_ids.append(pk)
        else:
            seen_users.add(user_id)

    if duplicate_ids:
        settings.filter(pk__in=duplicate_ids).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("beltradar", "0013_alter_evemarketprice_adjusted_price"),
    ]

    operations = [
        migrations.RunPython(
            remove_invalid_usersettings, reverse_code=migrations.RunPython.noop
        ),
    ]
