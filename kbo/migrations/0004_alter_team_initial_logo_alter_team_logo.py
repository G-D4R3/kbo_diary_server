# Generated by Django 5.0.4 on 2024-08-12 08:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("kbo", "0003_alter_team_initial_logo_alter_team_logo"),
    ]

    operations = [
        migrations.AlterField(
            model_name="team",
            name="initial_logo",
            field=models.ImageField(null=True, upload_to="team_initial_logos/"),
        ),
        migrations.AlterField(
            model_name="team",
            name="logo",
            field=models.ImageField(null=True, upload_to="team_logos/"),
        ),
    ]
