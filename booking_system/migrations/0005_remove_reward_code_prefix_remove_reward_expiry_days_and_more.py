# Generated by Django 5.1.3 on 2025-05-03 15:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("booking_system", "0004_reward_userreward"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="reward",
            name="code_prefix",
        ),
        migrations.RemoveField(
            model_name="reward",
            name="expiry_days",
        ),
        migrations.RemoveField(
            model_name="userreward",
            name="used_at",
        ),
    ]
