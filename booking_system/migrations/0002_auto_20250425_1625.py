from django.db import migrations


def create_profiles(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('booking_system', 'UserProfile')

    for user in User.objects.all():
        UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'phone_number': '',
                'gender': ''
            }
        )


class Migration(migrations.Migration):
    dependencies = [
        ('booking_system', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_profiles),
    ]