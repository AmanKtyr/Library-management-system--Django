# Generated by Django 5.2 on 2025-04-30 13:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libraries', '0002_librarysettings'),
    ]

    operations = [
        migrations.DeleteModel(
            name='LibrarySettings',
        ),
    ]
