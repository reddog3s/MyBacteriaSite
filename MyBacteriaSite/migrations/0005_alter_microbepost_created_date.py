# Generated by Django 4.1.7 on 2023-05-04 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("MyBacteriaSite", "0004_alter_microbepost_microbe"),
    ]

    operations = [
        migrations.AlterField(
            model_name="microbepost",
            name="created_date",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
